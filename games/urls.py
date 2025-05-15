from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('<str:game_name>/', views.game_room, name='game_room'),
    path('<int:game_id>/state/', views.game_state, name='game_state'),
    path('<int:game_id>/move/', views.make_move, name='make_move'),
] 