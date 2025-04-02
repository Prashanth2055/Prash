from django.urls import path
from . import views

urlpatterns = [   
    path('',views.home, name="home"),
    path('about/',views.about, name="about"),
    path('contact/',views.contact, name="contact"),
    path('login/',views.handlelogin, name="handlelogin"),
    path('search/',views.search, name="search"),
    path('logout',views.handlelogout, name="handlelogout"),
    path('signup/',views.handlesignup, name="handlesignup"),
    path('blog/',views.handleblog, name="handleblog"),
    path('services/',views.services,name="services"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/',views.update_profile,name="profile"),
    path('resetpassword/',views.resetpassword,name="resetpassword"),
    path('accounts/reset/<uidb64>/<token>/', views.manual_password_reset_confirm, name="changepassword"),
    path("confirm-email-update/<uidb64>/<token>/<new_email>/", views.confirm_email_update, name="confirm_email_update"),

]
