from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import SteganographyOperation
from .utils import (
    encode_message_in_image, decode_message_from_image,
    encode_pdf_in_image, decode_pdf_from_image,
    image_to_base64
)
import os
import mimetypes
import uuid

@login_required
def dashboard(request):
    """
    Affiche le tableau de bord avec les options de stéganographie.
    """
    return render(request, 'steganography/dashboard.html')

@login_required
def encrypt_message(request):
    """
    Gère le chiffrement d'un message dans une image.
    """
    if request.method == 'POST':
        message = request.POST.get('message')
        password = request.POST.get('password')
        image = request.FILES.get('image')
        
        if not message or not password or not image:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'steganography/encrypt_message.html')
        
        # Sauvegarde temporaire de l'image
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'original', f"{uuid.uuid4()}_{image.name}")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        try:
            # Encodage du message dans l'image
            result_path = encode_message_in_image(image_path, message, password)
            
            # Création d'une entrée dans l'historique
            operation = SteganographyOperation.objects.create(
                user=request.user,
                operation_type='encrypt_message',
                original_file=os.path.basename(image_path),
                result_file=os.path.basename(result_path),
                file_name=os.path.basename(image_path),
                file_size=os.path.getsize(image_path)
            )
            
            # Conversion de l'image en base64 pour l'affichage
            original_image_b64 = image_to_base64(image_path)
            result_image_b64 = image_to_base64(result_path)
            
            context = {
                'operation': operation,
                'original_image': original_image_b64,
                'result_image': result_image_b64,
                'download_url': reverse('steganography:download_result', args=[operation.id])
            }
            
            return render(request, 'steganography/encrypt_message_result.html', context)
            
        except Exception as e:
            messages.error(request, f"Erreur lors du chiffrement : {str(e)}")
            return render(request, 'steganography/encrypt_message.html')
    
    return render(request, 'steganography/encrypt_message.html')

@login_required
def decrypt_message(request):
    """
    Gère le déchiffrement d'un message depuis une image.
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        image = request.FILES.get('image')
        
        if not password or not image:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'steganography/decrypt_message.html')
        
        # Sauvegarde temporaire de l'image
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', f"{uuid.uuid4()}_{image.name}")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        try:
            # Décodage du message depuis l'image
            message = decode_message_from_image(image_path, password)
            
            # Création d'une entrée dans l'historique
            operation = SteganographyOperation.objects.create(
                user=request.user,
                operation_type='decrypt_message',
                original_file=os.path.basename(image_path),
                file_name=os.path.basename(image_path),
                file_size=os.path.getsize(image_path)
            )
            
            # Conversion de l'image en base64 pour l'affichage
            image_b64 = image_to_base64(image_path)
            
            context = {
                'operation': operation,
                'image': image_b64,
                'message': message
            }
            
            return render(request, 'steganography/decrypt_message_result.html', context)
            
        except Exception as e:
            messages.error(request, f"Erreur lors du déchiffrement : {str(e)}")
            return render(request, 'steganography/decrypt_message.html')
    
    return render(request, 'steganography/decrypt_message.html')

@login_required
def encrypt_pdf(request):
    """
    Gère le chiffrement d'un PDF dans une image.
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        image = request.FILES.get('image')
        pdf = request.FILES.get('pdf')
        
        if not password or not image or not pdf:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'steganography/encrypt_pdf.html')
        
        # Sauvegarde temporaire de l'image et du PDF
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'original', f"{uuid.uuid4()}_{image.name}")
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'original', f"{uuid.uuid4()}_{pdf.name}")
        
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf.chunks():
                destination.write(chunk)
        
        try:
            # Encodage du PDF dans l'image
            result_path = encode_pdf_in_image(image_path, pdf_path, password)
            
            # Création d'une entrée dans l'historique
            operation = SteganographyOperation.objects.create(
                user=request.user,
                operation_type='encrypt_pdf',
                original_file=os.path.basename(image_path),
                result_file=os.path.basename(result_path),
                file_name=os.path.basename(image_path),
                file_size=os.path.getsize(image_path)
            )
            
            # Conversion de l'image en base64 pour l'affichage
            original_image_b64 = image_to_base64(image_path)
            result_image_b64 = image_to_base64(result_path)
            
            context = {
                'operation': operation,
                'original_image': original_image_b64,
                'result_image': result_image_b64,
                'pdf_name': os.path.basename(pdf_path),
                'download_url': reverse('steganography:download_result', args=[operation.id])
            }
            
            return render(request, 'steganography/encrypt_pdf_result.html', context)
            
        except Exception as e:
            messages.error(request, f"Erreur lors du chiffrement : {str(e)}")
            return render(request, 'steganography/encrypt_pdf.html')
    
    return render(request, 'steganography/encrypt_pdf.html')

@login_required
def decrypt_pdf(request):
    """
    Gère le déchiffrement d'un PDF depuis une image.
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        image = request.FILES.get('image')
        
        if not password or not image:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'steganography/decrypt_pdf.html')
        
        # Sauvegarde temporaire de l'image
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'temp', f"{uuid.uuid4()}_{image.name}")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        try:
            # Décodage du PDF depuis l'image
            pdf_path = decode_pdf_from_image(image_path, password)
            
            # Création d'une entrée dans l'historique
            operation = SteganographyOperation.objects.create(
                user=request.user,
                operation_type='decrypt_pdf',
                original_file=os.path.basename(image_path),
                result_file=os.path.basename(pdf_path),
                file_name=os.path.basename(image_path),
                file_size=os.path.getsize(image_path)
            )
            
            # Conversion de l'image en base64 pour l'affichage
            image_b64 = image_to_base64(image_path)
            
            context = {
                'operation': operation,
                'image': image_b64,
                'pdf_path': pdf_path,
                'download_url': reverse('steganography:download_pdf', args=[operation.id])
            }
            
            return render(request, 'steganography/decrypt_pdf_result.html', context)
            
        except Exception as e:
            messages.error(request, f"Erreur lors du déchiffrement : {str(e)}")
            return render(request, 'steganography/decrypt_pdf.html')
    
    return render(request, 'steganography/decrypt_pdf.html')

@login_required
def download_result(request, operation_id):
    """
    Permet de télécharger le résultat d'une opération.
    """
    operation = get_object_or_404(SteganographyOperation, id=operation_id, user=request.user)
    
    if not operation.result_file:
        messages.error(request, "Aucun fichier résultat n'est disponible pour cette opération.")
        return redirect('history:history')
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'result', operation.result_file)
    
    if not os.path.exists(file_path):
        messages.error(request, "Le fichier demandé n'existe pas.")
        return redirect('history:history')
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{operation.result_file}"'
        return response

@login_required
def download_pdf(request, operation_id):
    """
    Permet de télécharger un PDF déchiffré.
    """
    operation = get_object_or_404(SteganographyOperation, id=operation_id, user=request.user)
    
    if not operation.result_file:
        messages.error(request, "Aucun fichier PDF n'est disponible pour cette opération.")
        return redirect('history:history')
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'result', operation.result_file)
    
    if not os.path.exists(file_path):
        messages.error(request, "Le fichier demandé n'existe pas.")
        return redirect('history:history')
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="decoded.pdf"'
        return response

@login_required
def history_view(request):
    """
    Affiche l'historique des opérations de l'utilisateur.
    """
    operations = SteganographyOperation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history/history.html', {'operations': operations})

@login_required
def history_detail(request, operation_id):
    """
    Affiche les détails d'une opération.
    """
    operation = get_object_or_404(SteganographyOperation, id=operation_id, user=request.user)
    
    context = {
        'operation': operation
    }
    
    # Ajout des images en base64 si disponibles
    if operation.original_file:
        original_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'original', operation.original_file)
        if os.path.exists(original_path):
            context['original_image'] = image_to_base64(original_path)
    
    if operation.result_file:
        result_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'result', operation.result_file)
        if os.path.exists(result_path):
            context['result_image'] = image_to_base64(result_path)
    
    return render(request, 'history/detail.html', context)

@login_required
def history_delete(request, operation_id):
    """
    Supprime une opération de l'historique.
    """
    operation = get_object_or_404(SteganographyOperation, id=operation_id, user=request.user)
    
    if request.method == 'POST':
        # Suppression des fichiers associés
        if operation.original_file:
            original_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'original', operation.original_file)
            if os.path.exists(original_path):
                os.remove(original_path)
        
        if operation.result_file:
            result_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'result', operation.result_file)
            if os.path.exists(result_path):
                os.remove(result_path)
        
        # Suppression de l'opération
        operation.delete()
        
        messages.success(request, "L'opération a été supprimée avec succès.")
        return redirect('history:history')
    
    return render(request, 'history/delete_confirm.html', {'operation': operation})

