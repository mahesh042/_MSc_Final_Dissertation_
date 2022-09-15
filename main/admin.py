from email.headerregistry import Group
from django.conf import settings
from django.contrib import admin
from .models import DockStation,UserOTP,StripeCustomer,Booking,StripePasses,userhasbike,user_booking_history




admin.site.register(userhasbike)
admin.site.register(user_booking_history)

admin.site.register(StripeCustomer)


@admin.register(DockStation)
class DockStationAdmin(admin.ModelAdmin):
    list_display = ('name','address','postcode','landmark','image','total_docks','bikes_availible','dropoff_docks','latitude', 'longitude',)
    search_fields = ('postcode',)

    fieldsets = (
        (None, {
            'fields': ( 'name','address','postcode','landmark','image','total_docks','bikes_availible','dropoff_docks','latitude', 'longitude',)
        }),
    )

    class Media:
        if hasattr(settings, 'GOOGLE_MAPS_API_KEY') and settings.GOOGLE_MAPS_API_KEY:
            css = {
                'all': ('css/admin/location_picker.css',),
            }
            js = (
                'https://maps.googleapis.com/maps/api/js?key={}'.format(settings.GOOGLE_MAPS_API_KEY),
                'js/admin/location_picker.js',
            )

