from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Game


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


User = get_user_model()

class GameSerializer(serializers.ModelSerializer):
    # Custom field to get the player's usernames
    player1 = serializers.CharField(source='player1.username')
    player2 = serializers.CharField(source='player2.username')
    current_turn = serializers.CharField(source='current_turn.username', required=False)

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'current_turn', 'game_board', 'winner', 'draw']

    def update(self, instance, validated_data):
        # You can add custom update logic here if needed
        instance.game_board = validated_data.get('game_board', instance.game_board)
        instance.current_turn = validated_data.get('current_turn', instance.current_turn)
        instance.winner = validated_data.get('winner', instance.winner)
        instance.draw = validated_data.get('draw', instance.draw)
        instance.save()
        return instance
