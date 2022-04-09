from django.urls import path
from django.contrib import admin
from . import views
admin.site.site_header = 'Bike sharing app manager panel'
admin.site.site_title = 'BikeApp admin'
admin.site.site_url = 'http://127.0.0.1:8000/'
admin.site.index_title = 'bikeapp administration'

app_name = "main"   


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("signin/", views.signin_request, name="signin"),
    path('logout/',views.logout_request, name='logout'),
    path("register/", views.register_request, name="register"),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path("contact/", views.contact_us, name="contact"),
    path("success/", views.successView, name="success"),
    path("bookings/", views.bookings, name="bookings"),
    path('search/get/' , views.search , name="search"),
    path('postcodesearch/',views.postcodesearch,name = 'postcodesearch'),

]