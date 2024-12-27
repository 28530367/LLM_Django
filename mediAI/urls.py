from django.urls import path
from . import views

urlpatterns = [
    path('chatgpt/', views.chatgpt),
    path('ajax_submit/', views.ajax_submit),
]