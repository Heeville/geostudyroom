from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .serializers import ProfileSerializer
from django.contrib.auth.hashers import make_password

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Create your views here.

class SignupAPIView(APIView):
    def post(self,request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            hashed_password = make_password(password)  # 비밀번호 암호화
            validated_data['password'] = hashed_password  # 암호화된 비밀번호로 교체
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginAPIView(APIView):
    def post(self,request):
        schoolnumber=request.data.get('schoolnumber')
        password=request.data.get('password')
        user=authenticate(request,schoolnumber=schoolnumber,password=password)
        if user:
            login(request,user)
            serializer=ProfileSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'detail': '아이디는 학번, 비밀번호는 이름(한글) 입니다.'},status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutAPIView(APIView):
    def get(self,request):
        logout(request)
        return Response({'detail':'로그아웃 되었습니다.'},status=status.HTTP_200_OK)