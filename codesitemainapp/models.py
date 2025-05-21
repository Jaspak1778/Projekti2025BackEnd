#Malli luokat
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings

#CustomUserModel

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'   #override : ylikirjoitettu käyttäjätunnus kenttä joka peritty Abstract User mallista
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)
    

# Foorumi
class Aihealue(models.Model):  
    header = models.TextField()



class Ketju(models.Model):
    header = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_threads") #jos käyttäjä poistetaan niin ks käyttäjän julkaisut poistuu
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    aihealue = models.ForeignKey(Aihealue, on_delete=models.CASCADE, related_name="threads")

    def __str__(self):
        return self.header   #self.header Palauttaa otsikon object() sijaan

class Vastaus(models.Model):  
    content = models.TextField()
    replier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="forum_replies") #jos käyttäjä poistetaan niin ks käyttäjän julkaisut poistetaan.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ketju = models.ForeignKey(Ketju, on_delete=models.CASCADE, related_name="replies")  #jos alkuperäinen julkaisu poistetaan sen julkaisun vastaukset poistetaan.

    def __str__(self):
        return self.content[:35]   #Palauttaa otsikon object() sijaan ja ensimmäiset 35 merkkiä (preview)
#Notes osio
class Tags(models.TextChoices):
    C_SHARP = 'csharp', 'C#'
    REACT = 'react', 'React'
    VISUAL_STUDIO = 'visual_studio', 'Visual Studio'
    DJANGO = 'django', 'Django'
    PYTHON = 'python', 'Python'
    PERSONAL = 'personal', 

class Notes(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    header = models.TextField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.CharField(
        max_length=20,
        choices=Tags.choices,
        default=Tags.PERSONAL
    )
    def __str__(self):
        return self.header