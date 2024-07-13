
from django.urls import path, include
from . import views, HodViews



urlpatterns = [
    path('', views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('doLogin/', views.doLogin, name="doLogin"),
      path('register/', views.register, name='register'),
    path('get_user_details/', views.get_user_details, name="get_user_details"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('admin_home/', HodViews.admin_home, name="admin_home"),


    path('add_car/', HodViews.add_car, name="add_car"),
    # path('add_car_save/', HodViews.add_car_save, name="add_car_save"),
    path('manage_car/', HodViews.manage_car, name="manage_car"),
    path('edit_car/<int:car_id>/', HodViews.edit_car, name="edit_car"),
    # path('edit_car_save/', HodViews.edit_car_save, name="edit_car_save"),
    path('delete_car/<car_id>/', HodViews.delete_car, name="delete_car"),
    path('add_owner/', HodViews.add_owner, name="add_owner"),
    path('add_owner_save/', HodViews.add_owner_save, name="add_owner_save"),
    path('edit_owner/<owner_id>/', HodViews.edit_owner, name="edit_owner"),
    path('edit_owner_save/', HodViews.edit_owner_save, name="edit_owner_save"),
    path('manage_owner/', HodViews.manage_owner, name="manage_owner"),
    path('delete_owner/<owner_id>/', HodViews.delete_owner, name="delete_owner"),
    path('check_email_exist/', HodViews.check_email_exist, name="check_email_exist"),
    path('check_username_exist/', HodViews.check_username_exist, name="check_username_exist"),
    path('admin_profile/', HodViews.admin_profile, name="admin_profile"),
    path('admin_profile_update/', HodViews.admin_profile_update, name="admin_profile_update"),

    # Location Management URLs
    path('manage_location/', HodViews.manage_location, name="manage_location"),
    path('add_location/', HodViews.add_location, name="add_location"),
    path('add_location_save/', HodViews.add_location_save, name="add_location_save"),
    path('edit_location/<int:location_id>/', HodViews.edit_location, name="edit_location"),
    path('edit_location_save/', HodViews.edit_location_save, name="edit_location_save"),
    path('delete_location/<int:location_id>/', HodViews.delete_location, name="delete_location"),
    path('receive-location-data/', HodViews.receive_location_data, name='receive_location_data'),
    


]