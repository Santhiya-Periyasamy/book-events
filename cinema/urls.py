from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import custom_logout


urlpatterns = [
    path('', views.home, name='home'),  
    path('login/', views.custom_login, name='login'),
    path('signup/', views.custom_signup, name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    path('events/', views.all_events, name='all_events'),  
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('movies/', views.movie_list, name='movie_list'),
    path('concerts/', views.concert_list, name='concert_list'),
    path('movies/<int:movie_id>/shows/', views.show_list, name='show_list'),
    path('shows/', views.all_shows, name='all_shows'),
    path('search/', views.search_page, name='search_page'),
    path('shows/<int:show_id>/book/', views.book_show, name='book_show'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('booking/success/<str:booking_name>/<str:movie_title>/<int:seats>/', views.booking_success, name='booking_success'),
    ]
