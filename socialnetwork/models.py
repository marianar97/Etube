from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(blank=True, max_length=50)
    following = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
        return f'id={self.id}, bio="{self.bio}" user={self.user.id}'
    
class Playlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    total_mins = models.PositiveIntegerField()