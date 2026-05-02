"""
ROUTING VIEWS - Django Backend Proxy
Xử lý routing requests từ frontend, gọi API bên ngoài
"""

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings


# OpenRouteService API - Đọc từ settings.py
ORS_API_KEY = getattr(settings, 'ORS_API_KEY', '')
ORS_BASE_URL = 'https://api.openrouteservice.org/v2'

if not ORS_API_KEY:
    print("⚠️  WARNING: ORS_API_KEY chưa được cấu hình trong settings.py")

# OSRM Public (fallback)
OSRM_URL = 'https://router.project-osrm.org'


@csrf_exempt
@require_http_methods(['POST'])
def ors_directions(request):
    """
    Proxy ORS Directions API
    POST /api/routing/ors/directions/
    
    Body: {
        "coordinates": [[lng, lat], [lng, lat]],
        "profile": "driving-car"
    }
    """
    try:
        data = json.loads(request.body)
        coordinates = data.get('coordinates', [])
        profile = data.get('profile', 'driving-car')
        
        if len(coordinates) < 2:
            return JsonResponse({
                'error': 'Cần ít nhất 2 điểm'
            }, status=400)
        
        # Gọi ORS API
        url = f'{ORS_BASE_URL}/directions/{profile}'
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            'coordinates': coordinates,
            'instructions': True,
            'language': 'vi'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            # Fallback sang OSRM nếu ORS fail
            return osrm_fallback(coordinates, profile)
            
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def osrm_fallback(coordinates, profile):
    """Fallback sang OSRM khi ORS fail"""
    try:
        # Chuyển coordinates sang format OSRM
        coords_str = ';'.join([f"{c[0]},{c[1]}" for c in coordinates])
        
        # Map profile
        profile_map = {
            'driving-car': 'car',
            'cycling-regular': 'bike',
            'foot-walking': 'foot'
        }
        osrm_profile = profile_map.get(profile, 'car')
        
        url = f'{OSRM_URL}/route/v1/{osrm_profile}/{coords_str}?overview=full&geometries=geojson&steps=true'
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok':
                # Chuyển OSRM format sang ORS-like format
                route = data['routes'][0]
                
                # Lấy text hướng dẫn cơ bản từ OSRM steps
                steps_data = []
                if 'legs' in route and route['legs']:
                    osrm_steps = route['legs'][0].get('steps', [])
                    for step in osrm_steps:
                        instruction = ""
                        maneuver = step.get('maneuver', {})
                        if maneuver:
                            type_ = maneuver.get('type')
                            modifier = maneuver.get('modifier')
                            name = step.get('name', '')
                            name_text = f" vào {name}" if name else ""
                            
                            if type_ == 'turn':
                                instruction = f"Rẽ {modifier}{name_text}".replace('left', 'trái').replace('right', 'phải').replace('slight', 'hơi').replace('sharp', 'ngoặt')
                            elif type_ == 'new name' or type_ == 'continue':
                                instruction = f"Đi tiếp{name_text}"
                            elif type_ == 'depart':
                                instruction = f"Xuất phát{name_text}"
                            elif type_ == 'arrive':
                                instruction = "Đến nơi"
                            else:
                                instruction = f"Đi{name_text}"
                        
                        steps_data.append({
                            'instruction': instruction,
                            'name': step.get('name', '')
                        })

                return JsonResponse({
                    'routes': [{
                        'summary': {
                            'distance': route['distance'],
                            'duration': route['duration']
                        },
                        'geometry': {
                            'coordinates': route['geometry']['coordinates']
                        },
                        'segments': [{
                            'steps': steps_data
                        }]
                    }]
                })
        
        return JsonResponse({
            'error': 'Cả ORS và OSRM đều không khả dụng'
        }, status=503)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Fallback error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def geocode_address(request):
    """
    Geocoding địa chỉ -> tọa độ
    POST /api/routing/geocode/
    
    Body: {"address": "Hà Nội, Việt Nam"}
    """
    try:
        data = json.loads(request.body)
        address = data.get('address', '')
        
        if not address:
            return JsonResponse({'error': 'Thiếu địa chỉ'}, status=400)
        
        # Dùng Nominatim (OpenStreetMap)
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': address,
            'format': 'json',
            'limit': 5,
            'countrycodes': 'vn'
        }
        headers = {
            'User-Agent': 'QLDD-GIS/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            return JsonResponse({
                'results': [
                    {
                        'name': r['display_name'].split(',')[0],
                        'address': r['display_name'],
                        'lat': float(r['lat']),
                        'lng': float(r['lon'])
                    }
                    for r in results
                ]
            })
        
        return JsonResponse({'error': 'Geocoding failed'}, status=503)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def reverse_geocode(request):
    """
    Reverse geocoding: tọa độ -> địa chỉ
    POST /api/routing/reverse-geocode/
    
    Body: {"lat": 21.0285, "lng": 105.8542}
    """
    try:
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is None or lng is None:
            return JsonResponse({'error': 'Thiếu lat/lng'}, status=400)
        
        url = 'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': lat,
            'lon': lng,
            'format': 'json'
        }
        headers = {
            'User-Agent': 'QLDD-GIS/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return JsonResponse({
                'address': result.get('display_name', ''),
                'name': result.get('name', ''),
                'lat': lat,
                'lng': lng
            })
        
        return JsonResponse({'error': 'Reverse geocoding failed'}, status=503)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def routing_status(request):
    """
    Check status các routing services
    GET /api/routing/status/
    """
    status = {
        'ors': {'available': False, 'key_configured': bool(ORS_API_KEY)},
        'osrm': {'available': False},
        'nominatim': {'available': False}
    }
    
    # Test ORS
    try:
        test_url = f'{ORS_BASE_URL}/directions/driving-car'
        headers = {'Authorization': ORS_API_KEY}
        r = requests.post(test_url, json={'coordinates': [[105.85, 21.03], [105.86, 21.04]]}, 
                         headers=headers, timeout=5)
        status['ors']['available'] = r.status_code in [200, 401]  # 401 = key hợp lệ nhưng request sai
    except:
        pass
    
    # Test OSRM
    try:
        test_url = f'{OSRM_URL}/route/v1/car/105.85,21.03;105.86,21.04'
        r = requests.get(test_url, timeout=5)
        status['osrm']['available'] = r.status_code == 200
    except:
        pass
    
    # Test Nominatim
    try:
        test_url = 'https://nominatim.openstreetmap.org/search?q=Hanoi&format=json&limit=1'
        headers = {'User-Agent': 'QLDD-GIS/1.0'}
        r = requests.get(test_url, headers=headers, timeout=5)
        status['nominatim']['available'] = r.status_code == 200
    except:
        pass
    
    return JsonResponse({
        'services': status,
        'recommendation': 'ors' if status['ors']['available'] else ('osrm' if status['osrm']['available'] else 'none')
    })
