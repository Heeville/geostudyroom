from django.db.models import Count
from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from datetime import date,timedelta
from .models import Reservation, Rclock, StudyRoom
from .serializers import *
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

    
# Create your views here.
class ReservationAPIView(APIView):
    def get_rclock_from_time_str(self, time_str):
        try:
            return Rclock.objects.get(time=time_str)
        except Rclock.DoesNotExist:
            raise ValueError("올바른 시간 형식이 아닙니다.")
            
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'room': openapi.Schema(type=openapi.TYPE_STRING, description="스터디룸 이름(B,C)"),
                'date': openapi.Schema(type=openapi.TYPE_STRING, description="날짜: ex)2023-10-01"),
                'clock': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING, description="예약 시간-> ['1000pm','1030pm'] 처럼 배열 형식으로 주기")),
            }
        ),
        responses={
            201: openapi.Response('예약 생성 성공', ReservationSerializer),
            400: openapi.Response('예약 실패'),
        }
    )
    @csrf_exempt    
    def post(self, request):
        # 요청에서 필요한 데이터를 가져옵니다.
        room_name = request.data.get("room")
        date = request.data.get("date")
        clock_values = request.data.get("clock", [])

        # 스터디룸을 가져오거나 없으면 404 에러를 반환합니다.
        study_room = get_object_or_404(StudyRoom, name=room_name, date=date)

        # clock_values를 Rclock 모델의 객체로 변환합니다.
        clock_objects = [self.get_rclock_from_time_str(value) for value in clock_values]

        # 이미 해당 스터디룸, 날짜, 시간대에 예약이 있는지 확인합니다.
        existing_reservations = Reservation.objects.filter(
            room=study_room,
            date=date,
            clocks__in=clock_objects
        ).count()

        # 해당 시간대에 예약이 이미 있으면 에러 응답을 반환합니다.
        if existing_reservations > 0:
            return Response({"detail": "해당 일자, 스터디룸, 시각에 이미 예약이 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 유저가 해당 날짜에 이미 예약한 시간 수를 계산
        user = request.user
        reservations_on_date = Reservation.objects.filter(user=user, date=date) \
            .annotate(clock_count=Count('clocks')) \
            .first()

        # 하루에 최대 2시간까지 예약할 수 있는지 확인하고 예약을 생성합니다.
        if reservations_on_date and reservations_on_date.clock_count >= 4:
            return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 선택한 시간대에 대한 예약을 생성합니다.
        reservation = Reservation(user=user, room=study_room, date=date)
        reservation.save()

        # clock_objects 리스트에서 Rclock 모델의 객체를 clocks 필드에 추가합니다.
        reservation.clocks.set(clock_objects)

        for value in clock_values:
            time_str = value[:2]+value[3:]  # ":00"제거
            # 시간대를 기반으로 해당 시간대 필드를 업데이트
            setattr(study_room, f"time{time_str}", True)

        study_room.save()
        serializer=ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ReservationDetail(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('예약 상세 정보 조회 성공', ReservationSerializer),
            404: openapi.Response('예약 정보가 없음'),
        }
    )
    @csrf_exempt  
    def get(self,request,room_name, date):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        reservationdetail = get_object_or_404(Reservation, user=request.user, room=study_room)
        serializer=ReservationSerializer(reservationdetail)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class MyReservation(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('내 예약 목록 조회 성공', ReservationSerializer(many=True)),
        }
    )
    @csrf_exempt  
    def get(self,request):
        reservations=Reservation.objects.filter(user=request.user)
        serializer=ReservationSerializer(reservations,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    
'''class DeleteReservation(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('삭제할 에약 정보 조회 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
    def get(self,request,pk):
        delreservation=get_object_or_404(Reservation,user=request.user,pk=pk)
        serializer=ReservationSerializer(delreservation)
        delroom=delreservation.room
        deldate=delreservation.date
        room = str(delroom).split(':')[0]
        print(room)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('예약 삭제 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
        
    def delete(self,request,pk):
        delreservation=get_object_or_404(Reservation,user=request.user,pk=pk)
        delroom=delreservation.room
        deldate=delreservation.date
        room = str(delroom).split(':')[0]
        study_room=get_object_or_404(StudyRoom,name=room,date=deldate)
        clock_values = delreservation.clocks.all()   
        for value in clock_values:
            strr=value.time
            time_str = strr[:2]+strr[3:]# ":"제거
            print(time_str)
            # 시간대를 기반으로 해당 시간대 필드를 업데이트
            setattr(study_room, f"time{time_str}", False)
        
        study_room.save()
        delreservation.delete()
        
        return Response({'message': '스터디룸 예약 취소가 완료되었습니다.'}, status=200)'''
        
class DeleteReservation(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('삭제할 에약 정보 조회 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
    @csrf_exempt  
    def get(self,request,room_name, date):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        delreservation = get_object_or_404(Reservation, user=request.user, room=study_room)
        #delreservation=get_object_or_404(Reservation,user=request.user,room=room_name,date=date)
        serializer=ReservationSerializer(delreservation)
        delroom=delreservation.room
        deldate=delreservation.date
        room = str(delroom).split(':')[0]
        print(room)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('예약 삭제 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
    @csrf_exempt      
    def delete(self,request,room_name, date):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        delreservation = get_object_or_404(Reservation, user=request.user, room=study_room)
        #delreservation=get_object_or_404(Reservation,user=request.user,room=room_name,date=date)
        delroom=delreservation.room
        deldate=delreservation.date
        room = str(delroom).split(':')[0]
        study_room=get_object_or_404(StudyRoom,name=room,date=deldate)
        clock_values = delreservation.clocks.all()   
        for value in clock_values:
            strr=value.time
            time_str = strr[:2]+strr[3:]# ":"제거
            print(time_str)
            # 시간대를 기반으로 해당 시간대 필드를 업데이트
            setattr(study_room, f"time{time_str}", False)
        
        study_room.save()
        delreservation.delete()
        
        return Response({'message': '스터디룸 예약 취소가 완료되었습니다.'}, status=200)
        




class ReservationTable(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, 
            properties={
                'room': openapi.Schema(type=openapi.TYPE_STRING, description="스터디룸 이름(B,C)"),
                'date': openapi.Schema(type=openapi.TYPE_STRING, description="날짜: ex)2023-10-01 "),
            }
        ),
        responses = {
            201: openapi.Response('해당 날짜의 해당 스터디룸 예약현황 조회 성공', StudyroomSerializer),
            400: openapi.Response('해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다.')
        }
      )
    @csrf_exempt  
    def post(self,request):
        name=request.data.get('room')
        date=request.data.get('date')
        rstudy=get_object_or_404(StudyRoom, name=name, date=date)
        if rstudy:
            serializers=StudyroomSerializer(rstudy)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        return Response({"detail": "해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다."}, status=status.HTTP_400_BAD_REQUEST)


class CreateStudyRooms(APIView):
    def post(self, request):
        # name='B'인 스터디룸 생성
        study_room, created = StudyRoom.objects.get_or_create(name='C')

        # 2023년 9월 4일부터 2024년 8월 31일까지의 날짜 범위 생성
        start_date = date(2023, 9, 6)
        end_date = date(2024, 8, 31)
        delta = timedelta(days=1)

        current_date = start_date

        # 날짜 범위 내의 각 날짜에 대한 스터디룸 객체 생성
        while current_date <= end_date:
            StudyRoom.objects.create(name='C', date=current_date)
            current_date += delta

        return Response({"detail": "스터디룸 객체 생성이 완료되었습니다."}, status=status.HTTP_201_CREATED)
    
    
    
class ReservationListAPIView(generics.ListAPIView):  
    queryset=Reservation.objects.all()
    serializer_class=ReservationSerializer
        
    @swagger_auto_schema(
        responses={
            200: openapi.Response('모든 예약 정보 조회 성공', ReservationSerializer(many=True)),
        }
        )
            
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
