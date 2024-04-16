from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.CharField(max_length=500)
    content_type = models.CharField(blank=True, max_length=50)
    following = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
        return f'id={self.id}, user={self.user.id}'
    
class Channel(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    name = models.CharField(max_length=70)
    thumbnail =  models.CharField(max_length=300)

class Playlist(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    user = models.ManyToManyField(User)
    total_mins = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    thumbnail =  models.CharField(max_length=300)
    channel = models.ForeignKey(Channel, max_length=70, on_delete=models.PROTECT)

    def __str__(self):
        return f"id={self.id}, title={self.title}"

class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    user = models.ManyToManyField(User, through='UserCourse')
    total_mins = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    thumbnail =  models.CharField(max_length=300)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, max_length=70, on_delete=models.PROTECT)

    def __str__(self):
        return f"id={self.id}, title={self.title}"
    
class Video(models.Model):
    id = models.CharField(primary_key=True, max_length=300)
    total_mins = models.IntegerField()
    title = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    playlist = models.ManyToManyField(Playlist)
    course = models.ManyToManyField(Course, through='CourseVideo')

    def __str__(self):
        return f"id={self.id}, title={self.title}"

# class PlaylistVideo(models.Model):
#     video = models.ForeignKey(Video, on_delete=models.PROTECT)
#     playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT)
#     cur_secs = models.FloatField(default=0)
#     watched = models.BooleanField(default=0)

#     def __str__(self):
#         return f"playlist: {self.playlist.title}, video: {self.video.title}, cur_secs: {self.cur_secs}, watched: {self.watched}"


# class UserPlaylist(models.Model):
#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     playlist = models.ForeignKey(Playlist, on_delete=models.PROTECT)
#     perc_completed = models.FloatField(default=0)

#     def __str__(self):
#         return f"user: {self.user.username}, playlist: {self.playlist.title}, percentage completed: {self.perc_completed}"

class CourseVideo(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    video = models.ForeignKey(Video, on_delete=models.PROTECT)
    watched = models.BooleanField(default=0)
    cur_secs = models.IntegerField(default=0)
    position = models.IntegerField(null=False)

    def __str__(self):
        return f"course: {self.course.title}, video: {self.video.title}, watched: {self.watched}, current_seconds: {self.cur_secs}"

    class Meta:
        unique_together = ('course', 'video')

class UserCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    perc_completed = models.FloatField(default=0)

    def __str__(self):
        return f"course: {self.course.title}, user: {self.user.username}, % completed: {self.perc_completed}"    

    class Meta:
        unique_together = ('course', 'user')
        
