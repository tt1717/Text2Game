from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Game
import sys
sys.path.append('./game')
from doubutsu import GameState

# ひらがな⇔数値変換用マッピング
PIECE_TO_CHAR = {
    1: "ひ", 2: "キ", 3: "ゾ", 4: "ラ", 5: "に",
    -1: "ひ", -2: "キ", -3: "ゾ", -4: "ラ", -5: "に", 0: ""
}
CHAR_TO_PIECE = {v: k for k, v in PIECE_TO_CHAR.items()}

# ひらがな盤面→数値盤面
def char_board_to_int(board):
    return [[CHAR_TO_PIECE.get(cell, 0) for cell in row] for row in board]

# 数値盤面→ひらがな盤面
def int_board_to_char(board):
    return [[PIECE_TO_CHAR.get(cell, "") for cell in row] for row in board]

# ひらがな持ち駒→数値持ち駒
def char_hand_to_int(hand):
    return [CHAR_TO_PIECE.get(piece, 0) if isinstance(piece, str) else piece for piece in hand]

def to_int_board(board):
    return [[int(cell) for cell in row] for row in board]

def to_int_hand(hand):
    return [int(piece) for piece in hand]

# Create your views here.

def game_list(request):
    games = Game.objects.all().order_by('-created_at')
    return render(request, 'game_app/game_list.html', {'games': games})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    message = ""
    # board, pieces_in_handをint型に変換
    int_board = to_int_board(game.board)
    int_hand_true = to_int_hand(game.pieces_in_hand.get("True", []))
    int_hand_false = to_int_hand(game.pieces_in_hand.get("False", []))
    # GameStateの復元
    state = GameState(
        board=int_board,
        pieces_in_hand={
            True: int_hand_true,
            False: int_hand_false
        },
        depth=game.depth
    )
    # --- デバッグ情報ここから ---
    if request.method == 'POST':
        is_drop = request.POST.get('is_drop') == 'true'
        if is_drop:
            drop_piece = int(request.POST.get('drop_piece'))
            to_y = int(request.POST.get('to_y'))
            to_x = int(request.POST.get('to_x'))
            action = ('drop', drop_piece, to_y, to_x)
        else:
            from_y = int(request.POST.get('from_y'))
            from_x = int(request.POST.get('from_x'))
            to_y = int(request.POST.get('to_y'))
            to_x = int(request.POST.get('to_x'))
            action = ('move', from_y, from_x, to_y, to_x)
        legal = state.legal_actions()
        if action in legal:
            state = state.next(action)
            game.board = state.board
            game.pieces_in_hand = {"True": state.pieces_in_hand[True], "False": state.pieces_in_hand[False]}
            game.depth += 1
            game.save()
            message = "コマを動かしました"
        else:
            message = "不正な手です"
    # --- デバッグ情報ここまで ---
    # 勝敗判定
    winner = state.get_winner()
    if winner:
        if winner == 'first':
            message = "先手の勝ちです！"
        elif winner == 'second':
            message = "後手の勝ちです！"
        elif winner == 'draw':
            message = "千日手（引き分け）です！"
        return render(request, 'game_app/game_detail.html', {'game': game, 'message': message, 'game_ended': True})
    return render(request, 'game_app/game_detail.html', {'game': game, 'message': message, 'game_ended': False})

def reset_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    game.initialize_board()
    return redirect('game_app:game_detail', pk=pk)
