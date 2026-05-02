"""
ROUTING URLS
API endpoints cho routing từ Django backend
"""

from django.urls import path
from myapp.views.routing_views import (
    ors_directions,
    geocode_address,
    reverse_geocode,
    routing_status
)

urlpatterns = [
    # ORS Directions (với fallback)
    path('api/routing/ors/directions/', ors_directions, name='ors_directions'),
    
    # Geocoding
    path('api/routing/geocode/', geocode_address, name='geocode_address'),
    path('api/routing/reverse-geocode/', reverse_geocode, name='reverse_geocode'),
    
    # Status check
    path('api/routing/status/', routing_status, name='routing_status'),
]
