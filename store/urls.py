from django.urls import path
from . import views
from .views import calculate_shipping

urlpatterns = [
        #Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
    path('update_size/', views.updateSize, name='update_size'),
	path('process_order/', views.processOrder, name="process_order"),
	path('login.html', views.loginview, name='login'),
	path('AboutUs.html', views.AboutUs, name='AboutUs'),
    path('calculate_shipping/', calculate_shipping, name='calculate_shipping'),
    # path('helcim', include('helcim.urls')),

    
]	
