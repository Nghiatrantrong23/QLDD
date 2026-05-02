import os
import sys
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from django.test import Client
c = Client()
c.login() # wait, login_required is on these views!
# I can just call the view directly, but mocking the request might be tricky.
# I'll just copy the view logic to see if it raises.
from myapp.models import VungQuyHoach, ThuaDat

def test_api():
    zones = []
    for vung in VungQuyHoach.objects.all():
        if vung.geom:
            try:
                g = json.loads(vung.geom.geojson)
                zones.append(g)
            except Exception as e:
                print("Error zone:", e)
    
    parcels = []
    for thua in ThuaDat.objects.all():
        if thua.mpoly:
            try:
                g = json.loads(thua.mpoly.geojson)
                parcels.append(g)
            except Exception as e:
                print("Error parcel:", e)

    print(f"Loaded {len(zones)} zones geometries")
    print(f"Loaded {len(parcels)} parcels geometries")

if __name__=='__main__':
    test_api()
