from django.db import models
from geouser.models import Profile
from django.utils import timezone

class Rclock(models.Model):
    time = models.CharField(max_length=15)

    def __str__(self):
        return self.time

# APIView에서 시간 문자열을 파싱하는 함수
def parse_time_str(time_str):
    return time_str

class StudyRoom(models.Model):
    name = models.CharField(max_length=10)
    date=models.DateField(blank=True,null=True)
    rclock = models.ManyToManyField(Rclock, related_name='reservateclock',blank=True)
    time12am=models.BooleanField(default=False)
    time01am=models.BooleanField(default=False)
    time02am=models.BooleanField(default=False)
    time03am=models.BooleanField(default=False)
    time04am=models.BooleanField(default=False)
    time05am=models.BooleanField(default=False)
    time06am=models.BooleanField(default=False)
    time07am=models.BooleanField(default=False)
    time08am=models.BooleanField(default=False)
    time09am=models.BooleanField(default=False)
    time10am=models.BooleanField(default=False)
    time11am=models.BooleanField(default=False)
    time12pm=models.BooleanField(default=False)
    time01pm=models.BooleanField(default=False)
    time02pm=models.BooleanField(default=False)
    time03pm=models.BooleanField(default=False)
    time04pm=models.BooleanField(default=False)
    time05pm=models.BooleanField(default=False)
    time06pm=models.BooleanField(default=False)
    time07pm=models.BooleanField(default=False)
    time08pm=models.BooleanField(default=False)
    time09pm=models.BooleanField(default=False)
    time10pm=models.BooleanField(default=False)
    time11pm=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}: {self.date}"

class Reservation(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    date = models.DateField()
    clocks = models.ManyToManyField(Rclock, related_name='reservations')

    def __str__(self):
        return f"{self.user}: {self.date}"
