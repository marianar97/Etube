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
    id = models.CharField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    total_mins = models.PositiveIntegerField()
    title = models.CharField()
    thumbnail =  models.CharField()
    ChannelId = models.CharField()
    UserId = models.CharField()

    def __str__(self):
        return f"id={self.id}, title={self.title}"

class video(models.Model):
    id = models.CharField(primary_key=True)
    total_mins = models.IntegerField()
    title = models.CharField()
    thumbnail = models.CharField()
    # channel = models.on

class Channel(models.Model):
    id = models.CharField(primary_key=True)
    name = models.CharField()
    thumbnail = models.CharField()



