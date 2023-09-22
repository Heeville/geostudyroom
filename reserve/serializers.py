from rest_framework import serializers
from .models import *
from geouser.models import *
from geouser.serializers import *

class StudyroomSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    class Meta:
        model=StudyRoom
        fields=['id','name','date','time']
        
    # "time_fields" 필드의 값을 설정하는 메서드를 정의합니다.
    def get_time(self, obj):
        time_fields = {}
        for field_name in obj._meta.get_fields():
            if field_name.name.startswith('time'):
                # "time"으로 시작하는 필드 이름에서 "time" 부분을 제거하고 사용합니다.
                short_field_name = field_name.name[4:6]+":"+ field_name.name[6:]
                time_fields[short_field_name] = getattr(obj, field_name.name)
        return time_fields
        
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
