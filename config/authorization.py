from rest_framework.authentication import SessionAuthentication

class CSRFExcemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass
    
    