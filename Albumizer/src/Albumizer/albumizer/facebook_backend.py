from django.contrib.auth import backends
from models import FacebookProfile


class FacebookBackend(backends.ModelBackend):
    def authenticate(self, facebookID=None):
        if facebookID:
            profiles = FacebookProfile.objects.all().filter(facebookID=facebookID)[:1]
            profile = profiles[0] if profiles else None
            if profile:
                return profile.userProfile.user

