from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .serializers import ProfileSerializer,UserinfoSerializer
from django.contrib.auth.hashers import make_password
from .models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@csrf_exempt
def deco(requset):
    return HttpResponse("success")

# Create your views here.

class SignupAPIView(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, 
            properties={
                'schoolnumber': openapi.Schema(type=openapi.TYPE_STRING, description="학번"),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="이름"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="비밀번호(이름 한글로)"),
            }
        ),
        responses = {
            201: openapi.Response('회원가입 성공', ProfileSerializer),
            400: openapi.Response('회원가입 실패')
        }
      )
      
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
    @swagger_auto_schema(
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    'schoolnumber': openapi.Schema(type=openapi.TYPE_STRING, description="학번"),
                    'password': openapi.Schema(type=openapi.TYPE_STRING, description="이름(한글로 적기)")
                }
            ),
            responses = {
                200: openapi.Response('로그인 성공', ProfileSerializer),
                400: openapi.Response('로그인 실패: 이미 다른 유저로 로그인 되어있습니다.'),
                401: openapi.Response('로그인 실패: 아이디는 학번, 비밀번호는 이름(한글) 입니다.')
            }
        )
    
    @csrf_exempt
    def post(self,request):
        if not isinstance(request.user, AnonymousUser):
            return Response({'detail': '이미 로그인되어 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        schoolnumber=request.data.get('schoolnumber')
        password=request.data.get('password')
        user=authenticate(request,schoolnumber=schoolnumber,password=password)
        #user=auth.authenticate(request,schoolnumber=schoolnumber,password=password)
        if user is not None:
            login(request,user)
            token, _ = Token.objects.get_or_create(user=user)
            serializer=ProfileSerializer(user)
            return Response({"message": "로그인 성공",
                             'token':token.key,
                             'pk':user.id,
                             'schoolnumber':user.schoolnumber,
                             'name':user.name
                            }, status=200)
            
            #return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'detail': '아이디는 학번, 비밀번호는 이름(한글) 입니다.'},status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutAPIView(APIView):
    
    @swagger_auto_schema(
            responses = {
                200: openapi.Response('로그아웃 성공')
            }
        )
    
    @csrf_exempt
    def get(self,request):
        logout(request)
        return Response({'detail':'로그아웃 되었습니다.'},status=status.HTTP_200_OK)
    
class MemberListAPIView(generics.ListAPIView):  
    queryset=Profile.objects.all()
    serializer_class=UserinfoSerializer
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('모든 학생 정보 조회 성공', UserinfoSerializer(many=True)),
        }
        )
        
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)