from django.db import models
from django.contrib.auth.models import User

class SteganographyOperation(models.Model):
    """Modèle pour stocker les opérations de stéganographie effectuées par les utilisateurs"""
    
    # Types d'opérations
    OPERATION_TYPES = (
        ('encrypt_message', 'Chiffrer un message dans une image'),
        ('decrypt_message', 'Déchiffrer un message depuis une image'),
        ('encrypt_pdf', 'Chiffrer un PDF en image'),
        ('decrypt_pdf', 'Déchiffrer une image en PDF'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Fichiers originaux et résultats
    original_file = models.FileField(upload_to='uploads/original/', null=True, blank=True)
    result_file = models.FileField(upload_to='uploads/result/', null=True, blank=True)
    
    # Métadonnées
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)  # Taille en octets
    is_successful = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_operation_type_display()} par {self.user.username} le {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']

