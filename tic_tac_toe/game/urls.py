from django.urls import path
from .views import RegisterView, LoginView
from . import views
from .views import StartGameView, MakeMoveView, GameHistoryView

urlpatterns = [

    # Routes for rendering the HTML pages
    path('register_page/', views.register_page, name='register_page'),
    path('login_page/', views.login_page, name='login_page'),
    path('index/', views.index, name='index'),

    # API views for login and registration
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('login/', views.LoginView.as_view(), name='api_login'),

    path('start_game/', StartGameView.as_view(), name='start_game'),
    path('make_move/', MakeMoveView.as_view(), name='make_move'),
    path('game_history/', GameHistoryView.as_view(), name='game_history'),
    path('update_profile/', views.UpdateProfileView.as_view(), name='update_profile'),
]
