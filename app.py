"""
Point d'entrée pour le déploiement de l'application SecureWatermark.
"""
import os
from securewatermark.wsgi import application

# Alias pour le déploiement
app = application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

