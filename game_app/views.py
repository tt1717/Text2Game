from django.shortcuts import render, get_object_or_404
from .models import Game

# Create your views here.

def game_list(request):
    games = Game.objects.all().order_by('-created_at')
    return render(request, 'game_app/game_list.html', {'games': games})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return render(request, 'game_app/game_detail.html', {'game': game})
