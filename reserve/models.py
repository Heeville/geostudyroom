from django.db import models
from geouser.models import Profile

class Rclock(models.Model):
    time = models.CharField(max_length=20)

    def __str__(self):
        return self.time

class StudyRoom(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    date = models.DateField()
    clocks = models.ManyToManyField(Rclock, related_name='reservations')

    def __str__(self):
        return f"{self.user}: {self.date}"
