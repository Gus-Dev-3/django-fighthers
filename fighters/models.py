from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class StarGGTournament(models.Model):
    url_tournament = models.URLField(max_length=200, blank=False, null= False)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.url_tournament
    

class ChallongeTournament(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Tamaño Máximo %sMB" % str(megabyte_limit))
        
    name = models.CharField(max_length=150 , blank=True)
    idTournament= models.CharField(max_length=20)
    is_completed = models.BooleanField(default=False)
    flayer_img = models.ImageField(upload_to='flayers/', blank=True, validators=[validate_image])
    game_name = models.CharField(max_length=70, blank=True)
    sign_up_url = models.URLField(max_length=150, blank=True)
    start_at = models.DateTimeField(null=True)
    stream_url = models.URLField(blank=True)
    def __str__(self):
        return self.name

class Post(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Tamaño Máximo %sMB" % str(megabyte_limit))
        
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    img_url = models.ImageField(upload_to='posts', blank=False, validators=[validate_image])


class StreamUser(models.Model):
    STREAMING_PLATFORMS = (
        ('TW', 'Twitch'),
        ('YT', 'YouTube'),
        ('FB', 'Facebook'),
    )
    
    user_name = models.CharField(max_length=150, blank=False)
    platform = models.CharField(max_length=2, choices=STREAMING_PLATFORMS, default='TW', blank=False)

    def __str__(self):
        return f"{self.user_name} - {self.get_platform_display()}"

