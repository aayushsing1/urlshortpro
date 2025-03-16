import geoip2.database
from django.conf import settings
import os

class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Load GeoIP2 database
        try:
            self.geoip_reader = geoip2.database.Reader(os.path.join(settings.GEOIP_PATH, 'GeoLite2-City.mmdb'))
        except FileNotFoundError:
            self.geoip_reader = None

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location_data(self, ip):
        if not self.geoip_reader:
            return None, None

        try:
            response = self.geoip_reader.city(ip)
            country = response.country.name
            city = response.city.name
            return country, city
        except:
            return None, None