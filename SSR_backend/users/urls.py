from django.urls import path

from users import views

urlpatterns = [
	path('login/', views.login),
	path('register/', views.register),
	path('logout/', views.logout),
	path('get/user/', views.get_current_user),
	path('set/psw/', views.change_password),
	path('reset/psw/', views.reset_password),
	path('confirm/', views.user_confirm),
	path('get/place/', views.get_user_places),
	path('get/device/', views.get_user_devices),
	path('get/device/all/',views.get_all_devices),
	path('get/device/single/',views.get_single_device),
	path('add/order/',views.add_user_order),
	path('get/order/', views.get_user_orders),
	path('set/place/',views.set_user_places),
	path('set/device/',views.set_user_devices),
	path('add/place/',views.add_user_places),
	path('add/device/',views.add_user_devices),
	path('delete/place/',views.delete_user_places),
	path('delete/device/',views.delete_user_devices),
	path('get/asset/',views.get_user_asset),
	path('set/asset/',views.set_user_asset),
	path('get/deal/',views.get_user_deal),
	path('add/deal/',views.add_user_deal),
	path('get/profile/',views.get_user_profile),
	# path('inject/order/',views.inject_orders_wrapper),
	# path('inject/place/',views.inject_places_wrapper),
	# path('inject/device/',views.inject_devices_wrapper),
]
