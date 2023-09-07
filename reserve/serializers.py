from rest_framework import serializers
from .models import *
from geouser.models import *
from geouser.serializers import *

class StudyroomSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudyRoom
        exclude=['rclock']
        
class ReservationSerializer(serializers.ModelSerializer):
    #schoolnumber=serializers.SerializerMethodField()
    #name=serializers.SerializerMethodField()
    user=ProfileSerializer()
    room=serializers.SerializerMethodField()
    clock_times=serializers.SerializerMethodField()
    class Meta:
        model=Reservation
        fields = ['id', 'user', 'room', 'date', 'clock_times']
        #fields=['id','schoolnumber','name','room','date','clock_times']
        
    #def get_schoolnumber(self,obj):
    #    return obj.user.schoolnumber
    
    #def get_name(self,obj):
     #   return obj.user.name

    def get_room(self,obj):
        return obj.room.name
    
    def get_clock_times(self,obj):
        clock_times = [clock.time for clock in obj.clocks.all()] 
        return clock_times
