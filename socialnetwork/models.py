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
    id = models.CharField(primary_key=True, max_length=300)
    user = models.ManyToManyField(User, null=True)
    total_mins = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    thumbnail =  models.CharField(max_length=300)
    channelId = models.CharField(max_length=70)

    def __str__(self):
        return f"id={self.id}, title={self.title}"

class Video(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    total_mins = models.IntegerField()
    title = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=300)
    playlist = models.ManyToManyField(Playlist)


class Channel(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    name = models.CharField(max_length=70)
    thumbnail = models.CharField(max_length=300)



