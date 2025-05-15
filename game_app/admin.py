from django.contrib import admin
from .models import Game

class GameAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.board:
            obj.initialize_board()
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Game, GameAdmin)
