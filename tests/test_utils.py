"""
Tests unitaires pour les fonctions de stéganographie et de chiffrement.
"""

import os
import pytest
import tempfile
from PIL import Image
import io
import base64
import json
from steganography.utils import (
    generate_key_from_password,
    encrypt_data,
    decrypt_data,
    image_to_base64
)

class TestCryptography:
    """Tests pour les fonctions de chiffrement."""
    
    def test_key_generation(self):
        """Test de la génération de clé à partir d'un mot de passe."""
        password = "test_password"
        key1, salt1 = generate_key_from_password(password)
        key2, salt2 = generate_key_from_password(password)
        
        # Les clés générées avec des sels différents doivent être différentes
        assert key1 != key2
        assert salt1 != salt2
        
        # La même clé doit être générée avec le même mot de passe et le même sel
        key3, _ = generate_key_from_password(password, salt1)
        assert key1 == key3
    
    def test_encrypt_decrypt(self):
        """Test du chiffrement et déchiffrement des données."""
        data = b"Test message for encryption and decryption"
        password = "test_password"
        
        # Chiffrement
        encrypted = encrypt_data(data, password)
        
        # Déchiffrement
        decrypted = decrypt_data(encrypted, password)
        
        # Vérification
        assert decrypted == data
        
        # Test avec un mot de passe incorrect
        with pytest.raises(ValueError):
            decrypt_data(encrypted, "wrong_password")

