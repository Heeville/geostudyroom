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
    time1200am=models.BooleanField(default=False)
    time1230am=models.BooleanField(default=False)
    time0100am=models.BooleanField(default=False)
    time0130am=models.BooleanField(default=False)
    time0200am=models.BooleanField(default=False)
    time0230am=models.BooleanField(default=False)
    time0300am=models.BooleanField(default=False)
    time0330am=models.BooleanField(default=False)
    time0400am=models.BooleanField(default=False)
    time0430am=models.BooleanField(default=False)
    time0500am=models.BooleanField(default=False)
    time0530am=models.BooleanField(default=False)
    time0600am=models.BooleanField(default=False)
    time0630am=models.BooleanField(default=False)
    time0700am=models.BooleanField(default=False)
    time0730am=models.BooleanField(default=False)
    time0800am=models.BooleanField(default=False)
    time0830am=models.BooleanField(default=False)
    time0900am=models.BooleanField(default=False)
    time0930am=models.BooleanField(default=False)
    time1000am=models.BooleanField(default=False)
    time1030am=models.BooleanField(default=False)
    time1100am=models.BooleanField(default=False)
    time1130am=models.BooleanField(default=False)
    time1200pm=models.BooleanField(default=False)
    time1230pm=models.BooleanField(default=False)
    time0100pm=models.BooleanField(default=False)
    time0130pm=models.BooleanField(default=False)
    time0200pm=models.BooleanField(default=False)
    time0230pm=models.BooleanField(default=False)
    time0300pm=models.BooleanField(default=False)
    time0330pm=models.BooleanField(default=False)
    time0400pm=models.BooleanField(default=False)
    time0430pm=models.BooleanField(default=False)
    time0500pm=models.BooleanField(default=False)
    time0530pm=models.BooleanField(default=False)
    time0600pm=models.BooleanField(default=False)
    time0630pm=models.BooleanField(default=False)
    time0700pm=models.BooleanField(default=False)
    time0730pm=models.BooleanField(default=False)
    time0800pm=models.BooleanField(default=False)
    time0830pm=models.BooleanField(default=False)
    time0900pm=models.BooleanField(default=False)
    time0930pm=models.BooleanField(default=False)
    time1000pm=models.BooleanField(default=False)
    time1030pm=models.BooleanField(default=False)
    time1100pm=models.BooleanField(default=False)
    time1130pm=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}: {self.date}"

class Reservation(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE)
    date = models.DateField()
    clocks = models.ManyToManyField(Rclock, related_name='reservations')

    def __str__(self):
        return f"{self.user}: {self.date}"
