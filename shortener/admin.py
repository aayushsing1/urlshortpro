from django.contrib import admin
from .models import Url , ClickData 
# Add to admin.py in the shortener app
from .models import DeviceTracker

admin.site.register(Url)
admin.site.register(ClickData)



@admin.register(DeviceTracker)
class DeviceTrackerAdmin(admin.ModelAdmin):
    list_display = ('url', 'device_identifier', 'last_earning_date')
    list_filter = ('last_earning_date',)
    search_fields = ('url__short_code', 'device_identifier')
    date_hierarchy = 'last_earning_date'
