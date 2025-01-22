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
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer, TokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


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

from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class MakeMoveView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    @transaction.atomic  # Ensure the move and turn switch happen atomically
    def post(self, request):
        game_id = request.data.get('game_id')
        position = request.data.get('position')

        if game_id is None or position is None:
            return Response({'error': 'Both game_id and position are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the game object using the provided game ID
        game = get_object_or_404(Game, id=game_id)

        # Debug log to check request user and players
        print(f"Authenticated User: {request.user.username}")
        print(f"Game ID: {game.id}, Player1: {game.player1.username}, Player2: {game.player2.username}")
        print(f"Current Turn before move: {game.current_turn.username}")

        # Check if the user is part of the game
        if request.user not in [game.player1, game.player2]:
            return Response({'error': 'You are not part of this game'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the game is still ongoing (no winner and no draw)
        if game.winner or game.draw:
            return Response({'error': 'Cannot update a completed game'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if it is the user's turn to play
        if game.current_turn != request.user:
            return Response({'error': 'It is not your turn'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate that the position is an integer and within the valid range (0-8)
            position = int(position)
            if position < 0 or position > 8:
                return Response({'error': 'Invalid position. Position must be between 0 and 8.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Process the move
            game.make_move(position, request.user)  # This calls the method that updates the board and game state

            # Log turn change
            print(f"Turn switched. New turn: {game.current_turn.username}")

            # Check if there is a winner or draw after the move
            if game.winner:
                return Response({'message': f'{game.winner.username} wins!'}, status=status.HTTP_200_OK)
            elif game.draw:
                return Response({'message': 'The game is a draw!'}, status=status.HTTP_200_OK)

            # Game is still ongoing, return updated game state
            return Response(GameSerializer(game).data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can update their profile

    def put(self, request):
        # Check if the user is authenticated
        if request.user.is_anonymous:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch the user from the request
        user = request.user

        # Update user profile with data from request
        username = request.data.get('username', user.username)
        email = request.data.get('email', user.email)

        # Optionally, update password (make sure it's hashed if updating)
        password = request.data.get('password', None)
        if password:
            user.set_password(password)

        # Save the user instance
        user.username = username
        user.email = email
        user.save()

        return Response({'message': 'Profile updated successfully!'}, status=status.HTTP_200_OK)