from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import importlib
import json
from .models import Game

# Create your views here.

def game_list(request):
    """利用可能なゲームの一覧を表示"""
    games = ['doubutsu', 'gobblet', 'quoridor', 'shogi', 'othello']
    return render(request, 'games/game_list.html', {'games': games})

def game_room(request, game_name):
    """特定のゲームのルームを表示"""
    try:
        # ゲームモジュールを動的にインポート
        game_module = importlib.import_module(f"game.{game_name}")
        GameState = getattr(game_module, 'GameState')
        
        # 新しいゲームを作成
        game_state = GameState()
        game = Game.objects.create(
            game_type=game_name,
            board_state=json.dumps(game_state.board),
            pieces_in_hand=json.dumps(game_state.pieces_in_hand)
        )
        
        return render(request, 'games/game_room.html', {
            'game_name': game_name,
            'game_title': game_name.capitalize(),
            'game_id': game.id,
            'initial_state': {
                'board': game_state.board,
                'pieces_in_hand': game_state.pieces_in_hand,
                'is_first_player': True
            }
        })
    except (ModuleNotFoundError, AttributeError):
        return JsonResponse({'error': f'Game {game_name} not found'}, status=404)

def game_state(request, game_id):
    """ゲームの状態を取得"""
    game = get_object_or_404(Game, id=game_id)
    return JsonResponse({
        'board': game.get_board_state(),
        'pieces_in_hand': game.get_pieces_in_hand(),
        'current_player': game.current_player
    })

def make_move(request, game_id):
    """手を打つ"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    game = get_object_or_404(Game, id=game_id)
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        # ゲームモジュールを動的にインポート
        game_module = importlib.import_module(f"game.{game.game_type}")
        GameState = getattr(game_module, 'GameState')
        
        # 現在の状態から新しい状態を作成
        current_state = GameState(
            board=game.get_board_state(),
            pieces_in_hand=game.get_pieces_in_hand()
        )
        
        # 手を適用
        new_state = current_state.next(action)
        
        # 状態を更新
        game.set_board_state(new_state.board)
        game.set_pieces_in_hand(new_state.pieces_in_hand)
        game.current_player = not game.current_player
        game.save()
        
        return JsonResponse({
            'success': True,
            'new_state': {
                'board': new_state.board,
                'pieces_in_hand': new_state.pieces_in_hand,
                'current_player': game.current_player
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
