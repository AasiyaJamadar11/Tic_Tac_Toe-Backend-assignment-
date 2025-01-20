from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Game, GameHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user and user.check_password(data['password']):
            return user
        raise serializers.ValidationError("Invalid credentials")

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class GameHistorySerializer(serializers.ModelSerializer):
    player = serializers.CharField(source='player.username')  # Serialize player's username

    class Meta:
        model = GameHistory
        fields = ['move_number', 'player', 'move']

class GameSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(source='player1.username')
    player2 = serializers.CharField(source='player2.username')
    current_turn = serializers.CharField(source='current_turn.username', required=False)
    winner = serializers.CharField(source='winner.username', required=False)
    draw = serializers.BooleanField()

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'current_turn', 'game_board', 'winner', 'draw']

    def create(self, validated_data):
        """Create a new game instance"""
        game = Game.objects.create(**validated_data)
        return game

    def update(self, instance, validated_data):
        """Update an existing game instance"""
        # Allow updates to the game board, current_turn, winner, or draw status
        instance.game_board = validated_data.get('game_board', instance.game_board)
        instance.current_turn = validated_data.get('current_turn', instance.current_turn)
        instance.winner = validated_data.get('winner', instance.winner)
        instance.draw = validated_data.get('draw', instance.draw)
        instance.save()
        return instance

    def validate_game_move(self, value):
        """Ensure that the move is valid. For example, make sure the move is within the valid range."""
        if value not in range(9):  # Tic-Tac-Toe has 9 positions
            raise serializers.ValidationError("Invalid move. Position must be between 0 and 8.")
        return value

    def validate(self, data):
        """Custom validation logic for making moves"""
        game = data.get('game', None)
        if not game:
            raise serializers.ValidationError("Game is not provided.")
        # Check if the move is allowed based on the current player's turn
        if game.current_turn != self.context['request'].user:
            raise serializers.ValidationError("It is not your turn to play.")
        return data
