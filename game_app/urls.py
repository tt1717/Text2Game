from django.urls import path
from . import views

app_name = 'game_app'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('game/<int:pk>/', views.game_detail, name='game_detail'),
    path('game/<int:pk>/reset/', views.reset_game, name='reset_game'),
] 