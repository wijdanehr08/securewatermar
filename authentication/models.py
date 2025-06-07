from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extension du modèle utilisateur de Django pour ajouter des champs supplémentaires"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"

