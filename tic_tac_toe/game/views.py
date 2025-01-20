from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer, TokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            token_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            token_serializer = TokenSerializer(token_data)
            return Response(token_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Game
from .serializers import GameSerializer  # Define this serializer for Game model

class StartGameView(APIView):
    def post(self, request):
        player1 = request.user
        player2 = User.objects.get(id=request.data['player2_id'])
        game = Game.objects.create(player1=player1, player2=player2, game_board=' ' * 9, current_turn=player1)
        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

class MakeMoveView(APIView):
    def post(self, request):
        game = Game.objects.get(id=request.data['game_id'])
        if game.current_turn == request.user:
            # Validate and update game board, check win/draw conditions
            return Response({'message': 'Move made successfully!'})
        return Response({'error': 'It is not your turn'}, status=status.HTTP_400_BAD_REQUEST)

class GameHistoryView(APIView):
    def get(self, request):
        history = GameHistory.objects.filter(game__player1=request.user)
        # Add logic to format this history appropriately
        return Response(history)

class UpdateProfileView(APIView):
    def put(self, request):
        user = request.user
        user.username = request.data.get('username', user.username)
        user.save()
        return Response({'message': 'Profile updated successfully!'})
