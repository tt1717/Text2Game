from django.db import models
import json

# Create your models here.

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    board = models.JSONField(default=list)  # 盤面情報（3x4のコマ配置）
    pieces_in_hand = models.JSONField(default=dict)  # 持ち駒情報
    depth = models.IntegerField(default=0)  # 手番管理用

    def __str__(self):
        return self.title

    def initialize_board(self):
        # どうぶつしょうぎの初期配置（数値）
        self.board = [
            [-2, -4, -3],
            [0,  -1,  0],
            [0,   1,  0],
            [3,   4,  2]
        ]
        self.pieces_in_hand = {"True": [], "False": []}
        self.depth = 0
        self.save()
