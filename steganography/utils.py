"""
Utilitaires pour les fonctionnalités de stéganographie et de chiffrement AES.
"""

import os
import base64
import json
import random
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import hashlib
import io

def generate_key_from_password(password, salt=None):
    """
    Génère une clé AES-256 à partir d'un mot de passe.
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Dérivation de clé à partir du mot de passe
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Nombre d'itérations
    )
    
    return key, salt

def encrypt_data(data, password):
    """
    Chiffre des données avec AES-256 en utilisant un mot de passe.
    """
    # Génération de la clé et du vecteur d'initialisation
    key, salt = generate_key_from_password(password)
    iv = os.urandom(16)
    
    # Préparation des données
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # Chiffrement
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Ajout du sel et du vecteur d'initialisation aux données chiffrées
    result = {
        'salt': base64.b64encode(salt).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8')
    }
    
    return json.dumps(result).encode('utf-8')

def decrypt_data(encrypted_package, password):
    """
    Déchiffre des données avec AES-256 en utilisant un mot de passe.
    """
    # Décodage du package chiffré
    try:
        package = json.loads(encrypted_package.decode('utf-8'))
        salt = base64.b64decode(package['salt'])
        iv = base64.b64decode(package['iv'])
        encrypted_data = base64.b64decode(package['encrypted_data'])
    except (json.JSONDecodeError, KeyError, base64.binascii.Error) as e:
        raise ValueError(f"Format de données chiffrées invalide: {str(e)}")
    
    # Génération de la clé à partir du mot de passe et du sel
    key, _ = generate_key_from_password(password, salt)
    
    # Déchiffrement
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Suppression du padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        data = unpadder.update(padded_data) + unpadder.finalize()
    except ValueError as e:
        raise ValueError(f"Mot de passe incorrect ou données corrompues: {str(e)}")
    
    return data

def encode_message_in_image(image_path, message, password):
    """
    Cache un message chiffré dans une image en utilisant la stéganographie LSB.
    """
    # Chiffrement du message
    encrypted_message = encrypt_data(message.encode('utf-8'), password)
    
    # Ouverture de l'image
    img = Image.open(image_path)
    width, height = img.size
    
    # Conversion en mode RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Vérification que l'image est assez grande pour contenir le message
    max_bytes = (width * height * 3) // 8
    if len(encrypted_message) > max_bytes - 4:
        raise ValueError(f"Le message est trop long pour cette image. Taille maximale: {max_bytes - 4} octets")
    
    # Conversion du message en bits
    message_size = len(encrypted_message)
    size_bits = format(message_size, '032b')
    message_bits = ''.join(format(byte, '08b') for byte in encrypted_message)
    
    # Insertion de la taille du message suivie du message
    data = size_bits + message_bits
    data_index = 0
    
    # Création d'une nouvelle image pour le résultat
    result_img = Image.new(img.mode, img.size)
    pixels = list(img.getdata())
    new_pixels = []
    
    for pixel in pixels:
        r, g, b = pixel
        
        # Modification des bits de poids faible si nécessaire
        if data_index < len(data):
            r = (r & 0xFE) | int(data[data_index])
            data_index += 1
        
        if data_index < len(data):
            g = (g & 0xFE) | int(data[data_index])
            data_index += 1
        
        if data_index < len(data):
            b = (b & 0xFE) | int(data[data_index])
            data_index += 1
        
        new_pixels.append((r, g, b))
    
    result_img.putdata(new_pixels)
    
    # Sauvegarde de l'image résultante
    result_path = os.path.join(os.path.dirname(image_path), '..', 'result', f"stegano_{os.path.basename(image_path)}")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    
    # Sauvegarde en PNG pour éviter la compression qui pourrait altérer les données
    if not result_path.lower().endswith('.png'):
        result_path = os.path.splitext(result_path)[0] + '.png'
    
    result_img.save(result_path, 'PNG')
    
    return result_path

def decode_message_from_image(image_path, password):
    """
    Extrait et déchiffre un message caché dans une image.
    """
    # Ouverture de l'image
    img = Image.open(image_path)
    
    # Conversion en mode RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Extraction des bits de poids faible
    pixels = list(img.getdata())
    binary_data = ''
    
    for pixel in pixels:
        r, g, b = pixel
        binary_data += str(r & 1)
        binary_data += str(g & 1)
        binary_data += str(b & 1)
    
    # Extraction de la taille du message
    message_size_bits = binary_data[:32]
    try:
        message_size = int(message_size_bits, 2)
    except ValueError:
        raise ValueError("Impossible de décoder la taille du message. L'image ne contient peut-être pas de message caché.")
    
    # Vérification que la taille est cohérente
    if message_size <= 0 or message_size > (len(binary_data) - 32) // 8:
        raise ValueError("Taille de message invalide détectée. L'image ne contient peut-être pas de message caché.")
    
    # Extraction du message
    message_bits = binary_data[32:32 + message_size * 8]
    
    # Conversion des bits en octets
    encrypted_message = bytearray()
    for i in range(0, len(message_bits), 8):
        if i + 8 <= len(message_bits):
            byte = message_bits[i:i+8]
            encrypted_message.append(int(byte, 2))
    
    # Déchiffrement du message
    try:
        decrypted_message = decrypt_data(bytes(encrypted_message), password)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Impossible de déchiffrer le message: {str(e)}. Vérifiez le mot de passe.")

def encode_pdf_in_image(image_path, pdf_path, password):
    """
    Cache un fichier PDF chiffré dans une image en utilisant la stéganographie LSB.
    """
    # Lecture du fichier PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    # Ajout du nom du fichier aux données
    pdf_name = os.path.basename(pdf_path)
    data_package = {
        'name': pdf_name,
        'content': base64.b64encode(pdf_data).decode('utf-8')
    }
    
    # Chiffrement des données
    encrypted_data = encrypt_data(json.dumps(data_package).encode('utf-8'), password)
    
    # Ouverture de l'image
    img = Image.open(image_path)
    width, height = img.size
    
    # Conversion en mode RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Vérification que l'image est assez grande pour contenir le PDF
    max_bytes = (width * height * 3) // 8
    if len(encrypted_data) > max_bytes - 4:
        raise ValueError(f"Le PDF est trop volumineux pour cette image. Taille maximale: {max_bytes - 4} octets")
    
    # Conversion des données en bits
    data_size = len(encrypted_data)
    size_bits = format(data_size, '032b')
    data_bits = ''.join(format(byte, '08b') for byte in encrypted_data)
    
    # Insertion de la taille des données suivie des données
    bits = size_bits + data_bits
    data_index = 0
    
    # Création d'une nouvelle image pour le résultat
    result_img = Image.new(img.mode, img.size)
    pixels = list(img.getdata())
    new_pixels = []
    
    for pixel in pixels:
        r, g, b = pixel
        
        # Modification des bits de poids faible si nécessaire
        if data_index < len(bits):
            r = (r & 0xFE) | int(bits[data_index])
            data_index += 1
        
        if data_index < len(bits):
            g = (g & 0xFE) | int(bits[data_index])
            data_index += 1
        
        if data_index < len(bits):
            b = (b & 0xFE) | int(bits[data_index])
            data_index += 1
        
        new_pixels.append((r, g, b))
    
    result_img.putdata(new_pixels)
    
    # Sauvegarde de l'image résultante
    result_path = os.path.join(os.path.dirname(image_path), '..', 'result', f"pdf_stegano_{os.path.basename(image_path)}")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    
    # Sauvegarde en PNG pour éviter la compression qui pourrait altérer les données
    if not result_path.lower().endswith('.png'):
        result_path = os.path.splitext(result_path)[0] + '.png'
    
    result_img.save(result_path, 'PNG')
    
    return result_path

def decode_pdf_from_image(image_path, password):
    """
    Extrait et déchiffre un fichier PDF caché dans une image.
    """
    # Ouverture de l'image
    img = Image.open(image_path)
    
    # Conversion en mode RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Extraction des bits de poids faible
    pixels = list(img.getdata())
    binary_data = ''
    
    for pixel in pixels:
        r, g, b = pixel
        binary_data += str(r & 1)
        binary_data += str(g & 1)
        binary_data += str(b & 1)
    
    # Extraction de la taille des données
    data_size_bits = binary_data[:32]
    try:
        data_size = int(data_size_bits, 2)
    except ValueError:
        raise ValueError("Impossible de décoder la taille des données. L'image ne contient peut-être pas de PDF caché.")
    
    # Vérification que la taille est cohérente
    if data_size <= 0 or data_size > (len(binary_data) - 32) // 8:
        raise ValueError("Taille de données invalide détectée. L'image ne contient peut-être pas de PDF caché.")
    
    # Extraction des données
    data_bits = binary_data[32:32 + data_size * 8]
    
    # Conversion des bits en octets
    encrypted_data = bytearray()
    for i in range(0, len(data_bits), 8):
        if i + 8 <= len(data_bits):
            byte = data_bits[i:i+8]
            encrypted_data.append(int(byte, 2))
    
    # Déchiffrement des données
    try:
        decrypted_data = decrypt_data(bytes(encrypted_data), password)
        data_package = json.loads(decrypted_data.decode('utf-8'))
        
        # Extraction du nom et du contenu du PDF
        pdf_name = data_package['name']
        pdf_content = base64.b64decode(data_package['content'])
        
        # Sauvegarde du PDF
        result_path = os.path.join(os.path.dirname(image_path), '..', 'result', f"decoded_{pdf_name}")
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        
        with open(result_path, 'wb') as f:
            f.write(pdf_content)
        
        return result_path
    except Exception as e:
        raise ValueError(f"Impossible de déchiffrer le PDF: {str(e)}. Vérifiez le mot de passe.")

def image_to_base64(image_path):
    """
    Convertit une image en chaîne base64 pour l'affichage dans un template HTML.
    """
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

