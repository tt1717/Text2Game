from django.urls import path
from . import views

app_name = 'game_app'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('<int:pk>/', views.game_detail, name='game_detail'),
] 