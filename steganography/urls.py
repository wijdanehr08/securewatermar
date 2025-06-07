from django.urls import path
from . import views

app_name = 'steganography'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('encrypt-message/', views.encrypt_message, name='encrypt_message'),
    path('decrypt-message/', views.decrypt_message, name='decrypt_message'),
    path('encrypt-pdf/', views.encrypt_pdf, name='encrypt_pdf'),
    path('decrypt-pdf/', views.decrypt_pdf, name='decrypt_pdf'),
]

