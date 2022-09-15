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
    path("complete/", views.complete, name="complete"),
    path("bookings/<int:id>", views.BookingView.as_view(), name="bookings"),
    path('stripe/create-checkout-session', views.create_checkout_session, name="stripe_create_checkout_session"), # new
    path('search/get/' , views.search , name="search"),
    path('postcodesearch/',views.postcodesearch,name = 'postcodesearch'),
    path('bikeavailibility/<int:id>', views.bikeavailibility, name="bikeavailibility"),
    path('mypass', views.mypass, name="mypass"),
    path('config/', views.stripe_config),
    path("user_bookings/", views.user_bookings, name="user_bookings"),
    path("booking_history", views.booking_history, name="booking_history"),
    path('webhook/', views.stripe_webhook),  # new
    path("cancel/", views.cancel, name="cancel"), #add this
    path("dropbike", views.dropbike, name="dropbike"), 
    path("pickbike", views.pickbike, name="pickbike"), 
    path("cancelled_transaction", views.cancelled_transaction, name="cancelled_transaction"), #add this

 
]