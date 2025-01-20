# game/views.py
from django.shortcuts import get_object_or_404
from .models import Game, GameHistory 
from .serializers import GameSerializer 
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer, TokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Game  # Add this import
from rest_framework.permissions import IsAuthenticated
from .serializers import GameHistorySerializer


User = get_user_model()

# game/views.py

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer, TokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

# Render login page
def login_page(request):
    return render(request, 'login.html')

# Render register page
def register_page(request):
    return render(request, 'register.html')

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



# Game-related views
class StartGameView(APIView):
    def post(self, request):
        # Extract player1 and player2 from the request data
        player1_id = request.data.get('player1')
        player2_id = request.data.get('player2')

        # Check if both players are provided
        if not player1_id or not player2_id:
            return Response({"error": "Both player1 and player2 are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get the users by their IDs
        try:
            player1 = User.objects.get(id=player1_id)
            player2 = User.objects.get(id=player2_id)
        except User.DoesNotExist:
            return Response({"error": "One or both players do not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure players are different
        if player1 == player2:
            return Response({"error": "Players must be different."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new game
        game = Game.objects.create(
            player1=player1,
            player2=player2,
            current_turn=player1,  # Player 1 starts the game
            game_board="         "  # Empty 3x3 board
        )

        # Return the game details using the GameSerializer
        return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)

class MakeMoveView(APIView):
    def post(self, request):
        game = get_object_or_404(Game, id=request.data['game_id'])
        if game.current_turn != request.user:
            return Response({'error': 'It is not your turn'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            position = int(request.data['position'])
            game.make_move(position, request.user)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if game.winner:
            return Response({'message': f'{game.winner.username} wins!'}, status=status.HTTP_200_OK)
        elif game.draw:
            return Response({'message': 'The game is a draw!'}, status=status.HTTP_200_OK)

        return Response(GameSerializer(game).data, status=status.HTTP_200_OK)

class GameHistoryView(APIView):
    permission_classes = [IsAuthenticated]  # This ensures the user is authenticated

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Fetch the game history of the current user (both as player1 and player2)
        games_as_player1 = Game.objects.filter(player1=request.user)
        games_as_player2 = Game.objects.filter(player2=request.user)
        games = games_as_player1 | games_as_player2
        
        if not games:
            return Response({"error": "No games found."}, status=status.HTTP_404_NOT_FOUND)

        game_histories = []

        for game in games:
            opponent = game.player2 if game.player1 == request.user else game.player1
            result = 'Draw' if game.draw else f'{game.winner.username} wins!' if game.winner else 'In Progress'
            
            # Get all the moves for this game
            moves = GameHistory.objects.filter(game=game).order_by('move_number')

            # Add the game details to the history list
            game_data = {
                'game_id': game.id,
                'opponent': opponent.username,
                'result': result,
                'moves': GameHistorySerializer(moves, many=True).data,
            }
            game_histories.append(game_data)
        
        return Response(game_histories, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    def put(self, request):
        user = request.user
        user.username = request.data.get('username', user.username)
        user.save()
        return Response({'message': 'Profile updated successfully!'})
