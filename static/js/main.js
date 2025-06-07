/**
 * SecureWatermark - Scripts principaux
 * Animations et interactions pour une expérience utilisateur premium
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animation des éléments avec la classe animate-slide-up
    const animateElements = document.querySelectorAll('.animate-slide-up');
    animateElements.forEach((element, index) => {
        // Ajoute un délai progressif pour créer un effet cascade
        if (!element.style.animationDelay) {
            element.style.animationDelay = `${index * 0.1}s`;
        }
    });
    
    // Effet de survol sur les boutons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.3)';
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Animation des liens de navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        link.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Animation du logo
    const logo = document.querySelector('.navbar-brand img');
    if (logo) {
        logo.addEventListener('mouseover', function() {
            this.style.transform = 'rotate(10deg)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        logo.addEventListener('mouseout', function() {
            this.style.transform = 'rotate(0)';
        });
    }
    
    // Animation des champs de formulaire
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 15px rgba(119, 141, 169, 0.7)';
            this.style.transition = 'box-shadow 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = 'none';
        });
    });
    
    // Animation des messages d'alerte
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Ajoute un effet de pulsation
        alert.style.animation = 'fadeIn 0.5s ease forwards, pulse 2s infinite';
        
        // Définition de l'animation de pulsation
        const style = document.createElement('style');
        style.innerHTML = `
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
    });
    
    // Effet de parallaxe pour les conteneurs principaux
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        
        // Effet de parallaxe sur les cartes
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const speed = 0.05;
            card.style.transform = `translateY(${scrollPosition * speed}px)`;
        });
    });
    
    // Animation des titres de section
    const sectionTitles = document.querySelectorAll('.card-header h2');
    sectionTitles.forEach(title => {
        title.style.position = 'relative';
        
        // Ajoute un effet de soulignement animé
        const underline = document.createElement('span');
        underline.style.position = 'absolute';
        underline.style.bottom = '-5px';
        underline.style.left = '50%';
        underline.style.width = '0';
        underline.style.height = '3px';
        underline.style.backgroundColor = 'var(--highlight-color)';
        underline.style.transform = 'translateX(-50%)';
        underline.style.transition = 'width 0.5s ease';
        
        title.appendChild(underline);
        
        title.addEventListener('mouseover', function() {
            underline.style.width = '80%';
        });
        
        title.addEventListener('mouseout', function() {
            underline.style.width = '0';
        });
    });
    
    // Animation des cartes au chargement
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        card.style.transitionDelay = `${index * 0.2}s`;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Effet de brillance au survol des cartes
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left; // Position X de la souris dans la carte
            const y = e.clientY - rect.top;  // Position Y de la souris dans la carte
            
            // Calcul de l'angle de la lumière en fonction de la position de la souris
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const angleX = (y - centerY) / 10;
            const angleY = (centerX - x) / 10;
            
            // Application de l'effet 3D
            this.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale(1.05)`;
            
            // Effet de brillance
            const shine = document.createElement('div');
            shine.style.position = 'absolute';
            shine.style.top = '0';
            shine.style.left = '0';
            shine.style.right = '0';
            shine.style.bottom = '0';
            shine.style.backgroundImage = `radial-gradient(circle at ${x}px ${y}px, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 80%)`;
            shine.style.pointerEvents = 'none';
            shine.classList.add('card-shine');
            
            // Supprime l'ancien effet de brillance s'il existe
            const oldShine = this.querySelector('.card-shine');
            if (oldShine) {
                this.removeChild(oldShine);
            }
            
            this.appendChild(shine);
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            
            // Supprime l'effet de brillance
            const shine = this.querySelector('.card-shine');
            if (shine) {
                this.removeChild(shine);
            }
        });
    });
});

