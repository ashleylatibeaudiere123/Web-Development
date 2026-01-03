from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    num_followers = models.IntegerField(default = 0)
    num_following = models.IntegerField(default = 0)
    followers = models.ManyToManyField('self', symmetrical = False, blank = True, related_name ="following")

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.CharField()
    likes = models.IntegerField(default = 0)
    liked_by = models.ManyToManyField(User, symmetrical = False, blank = True, null = True, related_name = "liked_posts")
    date_time = models.DateTimeField()



