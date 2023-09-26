from rest_framework import serializers
from .models import *

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model= Profile
        fields= ('schoolnumber', 'name','is_staff')
        