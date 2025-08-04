from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('predict/', views.predict, name='predict'),
    path('history/', views.history, name='history'),
    path('trends-api/', views.trends_api, name='trends_api'),
]