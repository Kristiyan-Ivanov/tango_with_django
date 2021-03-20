from django.urls import path
from rango import views
from rango.views import *
app_name = 'rango'


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/', ShowCategoryView.as_view(), name='show_category'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('category/<slug:category_name_slug>/add_page/', AddPageView.as_view(), name='add_page'),
    path('restricted/', views.restricted, name='restricted'),
    path('goto/', views.goto_page, name='goto'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('users/', ListUsersView.as_view(), name='users'),
]
