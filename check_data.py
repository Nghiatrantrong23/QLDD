import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import ThuaDat, VungQuyHoach
from django.db.models import Q

# Dem so ban ghi
tong_thua = ThuaDat.objects.count()
co_mpoly = ThuaDat.objects.filter(mpoly__isnull=False).count()
co_geojson = ThuaDat.objects.exclude(geojson_old__isnull=True).exclude(geojson_old='').count()
print(f"Tong thua dat: {tong_thua}")
print(f"Co mpoly: {co_mpoly}")
print(f"Co geojson_old: {co_geojson}")

# API filter
co_data = ThuaDat.objects.filter(
    Q(mpoly__isnull=False) | (Q(geojson_old__isnull=False) & ~Q(geojson_old__exact=''))
).count()
print(f"Se xuat hien trong API (co geometry): {co_data}")

# Thu lay 1 ban ghi va kiem tra
t = ThuaDat.objects.filter(mpoly__isnull=False).first()
if t:
    geom = json.loads(t.mpoly.geojson)
    gtype = geom.get("type")
    srid = t.mpoly.srid
    print(f"Sample: ma_thua={t.ma_thua}, geometry type={gtype}, SRID={srid}")
    if gtype == "MultiPolygon":
        first_coord = geom["coordinates"][0][0][0]
    elif gtype == "Polygon":
        first_coord = geom["coordinates"][0][0]
    else:
        first_coord = "unknown"
    print(f"First coordinate: {first_coord}")
else:
    print("CANH BAO: Khong co thu nao co mpoly!")

# Kiem tra quy hoach
tong_qh = VungQuyHoach.objects.count()
co_geom_qh = VungQuyHoach.objects.filter(geom__isnull=False).count()
chua_co_geom_qh = VungQuyHoach.objects.filter(geom__isnull=True).count()
print(f"\nTong quy hoach: {tong_qh}, co geom: {co_geom_qh}, chua co geom: {chua_co_geom_qh}")

if chua_co_geom_qh > 0:
    print("\n--- Dang tien hanh migration VungQuyHoach sang PostGIS geom ---")
    from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
    vung_loi = VungQuyHoach.objects.filter(geom__isnull=True).exclude(geojson_old__isnull=True).exclude(geojson_old__exact='')
    sl_migrated = 0
    for v in vung_loi:
        try:
            old_data = json.loads(v.geojson_old)
            if old_data.get('type') == 'FeatureCollection' and old_data.get('features'):
                geom_data = old_data['features'][0]['geometry']
            elif old_data.get('type') == 'Feature':
                geom_data = old_data['geometry']
            else:
                geom_data = old_data
                
            geom = GEOSGeometry(json.dumps(geom_data))
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom, srid=4326)
            if geom.geom_type == 'MultiPolygon':
                geom.srid = 4326
                v.geom = geom
                v.save()
                sl_migrated += 1
        except Exception as e:
            print(f"Loi migrate vung qh id={v.id}: {e}")
    print(f"Da migrate thanh cong: {sl_migrated} vung.")

# Simulate API response - check first feature
print("\n--- Simulate API response ---")
qs = ThuaDat.objects.select_related('chu_su_dung').filter(
    Q(mpoly__isnull=False) | (Q(geojson_old__isnull=False) & ~Q(geojson_old__exact=''))
)[:3]

for t in qs:
    geometry = None
    if t.mpoly:
        try:
            geometry = json.loads(t.mpoly.geojson)
        except Exception as e:
            print(f"  Loi parse mpoly geojson: {e}")
    elif t.geojson_old:
        try:
            geo_data = json.loads(t.geojson_old)
            if isinstance(geo_data, dict) and 'geometry' in geo_data:
                geometry = geo_data['geometry']
            elif isinstance(geo_data, dict) and 'type' in geo_data:
                geometry = geo_data
        except Exception as e:
            print(f"  Loi parse geojson_old: {e}")
    
    has_geom = geometry is not None
    geom_type = geometry.get('type') if geometry else 'None'
    print(f"  ma_thua={t.ma_thua}, loai_dat={t.loai_dat}, has_geom={has_geom}, geom_type={geom_type}")
