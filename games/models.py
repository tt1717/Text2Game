from django.db import models
import json

# Create your models here.

class Game(models.Model):
    game_type = models.CharField(max_length=20)  # ゲームの種類（doubutsu, gobblet等）
    board_state = models.TextField()  # 盤面の状態をJSONで保存
    pieces_in_hand = models.TextField()  # 持ち駒の状態をJSONで保存
    current_player = models.BooleanField(default=True)  # True: 先手, False: 後手
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_board_state(self, board):
        self.board_state = json.dumps(board)

    def get_board_state(self):
        return json.loads(self.board_state)

    def set_pieces_in_hand(self, pieces):
        self.pieces_in_hand = json.dumps(pieces)

    def get_pieces_in_hand(self):
        return json.loads(self.pieces_in_hand)
