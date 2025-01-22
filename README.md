# Tic_Tac_Toe-Backend-assignment-

Overview
This project is a Tic Tac Toe game backend built using Django. The application provides all the necessary APIs and logic to handle a Tic Tac Toe game, including move validation, game state management, and winner detection.

# Features
1. Backend logic to manage Tic Tac Toe gameplay.
2. APIs for making moves and checking game status.
3. Validates moves to prevent overwriting.
4. Determines the winner or a draw at the end of the game.

# Steps to Build and Run the App
# Prerequisites
Python (3.x)
Django (latest version recommended)
SQLite (default database for Django)

# Setup Instructions
1. Clone this repository or unzip the project folder:
git clone <repository-url>
cd tic_tac_toe

2. Create a virtual environment and activate it:
python -m venv env
source env/bin/activate  # For Windows: env\Scripts\activate

3. Install the dependencies:
pip install -r requirements.txt

4. Apply the database migrations:
python manage.py migrate

5. Run the development server:
python manage.py runserver

6. Use an API testing tool (such as Postman or curl) to interact with the backend APIs.

# App Architecture
The application is built using Django's MVT (Model-View-Template) pattern, although no frontend templates are included in this implementation.

Models: Defines the game state and stores player moves.
Views: Exposes APIs to handle game actions such as making moves and checking the game status.
URLs: Maps endpoints for the game APIs.

# Database Schema
The database is managed by Django’s ORM. You can find migrations in the migrations folder of the app.

# External Libraries or APIs Used
Django Framework: Used for backend logic, API creation, and database management.

# Assumptions and Incomplete Features
1. Assumptions:
The game logic assumes two players taking turns via API requests.
The backend does not include any frontend templates or user interface.

2. Incomplete Features:
Frontend integration for user interaction.
