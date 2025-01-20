from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Game(models.Model):
    player1 = models.ForeignKey(User, related_name='player1_games', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='player2_games', on_delete=models.CASCADE)
    current_turn = models.ForeignKey(User, related_name='turn_games', on_delete=models.SET_NULL, null=True)
    game_board = models.CharField(max_length=9)  # String to represent 3x3 board
    winner = models.ForeignKey(User, related_name='won_games', on_delete=models.SET_NULL, null=True, blank=True)
    draw = models.BooleanField(default=False)

    def __str__(self):
        return f'Game between {self.player1} and {self.player2}'

class GameHistory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    move_number = models.IntegerField()
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    move = models.CharField(max_length=3)  # Position on the board, e.g., '0', '1', '2'
