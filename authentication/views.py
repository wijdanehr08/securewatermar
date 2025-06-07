from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.db.models.query_utils import Q
from .models import UserProfile

def login_view(request):
    """Vue pour la page de connexion"""
    if request.user.is_authenticated:
        return redirect('/steganography/')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Gérer "Se souvenir de moi"
            if not remember_me:
                request.session.set_expiry(0)
                
            # Enregistrer l'adresse IP de connexion
            if hasattr(user, 'profile'):
                user.profile.last_login_ip = request.META.get('REMOTE_ADDR')
                user.profile.save()
            else:
                UserProfile.objects.create(
                    user=user,
                    last_login_ip=request.META.get('REMOTE_ADDR')
                )
                
            return redirect('/steganography/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'authentication/login.html')

def register_view(request):
    """Vue pour la page d'inscription"""
    if request.user.is_authenticated:
        return redirect('/steganography/')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Vérification des données
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'authentication/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà utilisé.")
            return render(request, 'authentication/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email est déjà utilisée.")
            return render(request, 'authentication/register.html')
        
        # Création de l'utilisateur
        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(
            user=user,
            last_login_ip=request.META.get('REMOTE_ADDR')
        )
        
        # Connexion automatique
        login(request, user)
        return redirect('/steganography/')
    
    return render(request, 'authentication/register.html')

def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    return redirect('/auth/login/')

def password_reset_request(request):
    """Vue pour la réinitialisation du mot de passe"""
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Réinitialisation de votre mot de passe"
                    email_template_name = "authentication/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'SecureWatermark',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@securewatermark.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/auth/password-reset/done/")
            messages.error(request, "Aucun compte n'est associé à cette adresse email.")
    password_reset_form = PasswordResetForm()
    return render(request, "authentication/password_reset.html", {"form": password_reset_form})

