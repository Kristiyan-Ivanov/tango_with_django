from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
path('', views.index, name='Index Page'),
path('about/', views.about, name='About Page')
]