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
    path('blog/',views.handleblog, name="handleblog")

]
