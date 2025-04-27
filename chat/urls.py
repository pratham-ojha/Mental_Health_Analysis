from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_response, name='chat'),  # This defines the main page for /chat
]
