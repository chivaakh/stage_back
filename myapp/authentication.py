# myapp/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Utilisateur

class CustomSessionAuthentication(BaseAuthentication):
    """
    Authentification basée sur l'ID utilisateur stocké en session
    """
    def authenticate(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return None
        
        try:
            user = Utilisateur.objects.get(id_utilisateur=user_id)
            return (user, None)  # (user, auth)
        except Utilisateur.DoesNotExist:
            raise AuthenticationFailed('Utilisateur invalide.')
    
    def authenticate_header(self, request):
        return 'Session'