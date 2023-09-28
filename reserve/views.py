from django.db.models import Count
from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from datetime import date,timedelta
from .models import Reservation, Rclock, StudyRoom
from .serializers import *
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
from django.utils.dateparse import parse_date
from datetime import datetime
from django.http import HttpResponse
import logging

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
            400: openapi.Response('예약 실패(사유:이미 예약이 있음)'),
            401: openapi.Response('예약 실패(사유:하루 최대 2시간까지 예약 가능)'),
            404: openapi.Response('사용자 정보를 찾을 수 없음'),
            406: openapi.Response('예약 실패(사유:하루 최대 2시간까지 예약 가능)'),
        }
    )
    @csrf_exempt    
    def post(self, request):
    # 요청에서 필요한 데이터를 가져옵니다
        # 요청에서 필요한 데이터를 가져옵니다.
        room_name = request.data.get("room")
        date_str = request.data.get("date")
        clock_values = request.data.get("clock", [])
        # 필수 필드(room, date, clock)가 누락되었는지 확인합니다.
        if not room_name or not date_str or not clock_values:
            return Response({"detail": "필수 필드 중 하나 이상이 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 날짜 형식 검증을 수행합니다.
        try:
            date = parse_date(date_str)
        except ValueError:
            raise ValueError("유효하지 않은 날짜 형식입니다.")

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
        user = request.user  #로그인 유지 성공했을때
        if not request.user.is_authenticated:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
        
        # 선택한 날짜에 대한 모든 예약을 가져옵니다.
        reservations_on_date = Reservation.objects.filter(user=user, date=date)
        total_clock_count = 0

        # 각 예약의 시간대 개수를 더합니다.
        for reservation in reservations_on_date:
            total_clock_count += reservation.clocks.count()
        
        #print(len(clock_values))
        #print(total_clock_count+len(clock_values))
        # 하루 최대 2시간까지 예약 가능한지 확인합니다.
        if (total_clock_count +len(clock_values))>4:
            return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        #currentcount=int(reservations_on_date and reservations_on_date.clock_count)+len(clock_values)
        #print(currentcount)
        
        #if currentcount>=4:
         #   return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_401_UNAUTHORIZED)

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
        
        reservationdetail = Reservation.objects.filter(room=study_room)
        serializer=ReservationSerializer(reservationdetail,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
       
class MyReservation(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('내 예약 목록 조회 성공', ReservationSerializer(many=True)),
            204: openapi.Response('내 예약 목록이 없음' ),
            404: openapi.Response('사용자 정보를 찾을 수 없음' ),
        }
    )
    @csrf_exempt  
    def get(self,request):
        if not request.user.is_authenticated:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
            #raise Http404("사용자 정보를 찾을 수 없습니다.") 
        reservations=Reservation.objects.filter(user=request.user).order_by('-date')
        if not reservations:
            return Response({'message': '예약한 목록이 없습니다.'}, status=status.HTTP_204_NO_CONTENT)

        serializer=ReservationSerializer(reservations,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

        
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
    def delete(self,request,room_name, date,clock_value):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        try:
            clock_value = Rclock.objects.get(time=clock_value)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        delreservation = Reservation.objects.filter(room__name=room_name, date=date, clocks__in=clock_values).first()
        #delreservation = get_object_or_404(Reservation, user=request.user, room=study_room)
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
    
class ReservationTableget(APIView):
    @swagger_auto_schema(
        responses = {
            201: openapi.Response('해당 날짜의 해당 스터디룸 예약테이블 조회 성공(date는 2023-12-31 형식으로 주세요)', StudyroomSerializer),
            400: openapi.Response('해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다.')
        }
      )
    @csrf_exempt  
    def get(self,request,room_name,date):
        name=room_name
        date=date
        rstudy=get_object_or_404(StudyRoom, name=name, date=date)
        if rstudy:
            serializers=StudyroomSerializer(rstudy)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        return Response({"detail": "해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다."}, status=status.HTTP_400_BAD_REQUEST)

class ReservationTable_clock(APIView):
    @swagger_auto_schema(
        responses = {
            201: openapi.Response('해당 스터디룸&날짜&시간의 예약현황 조회 성공(date는 2023-12-31,clock은 04:00pm 형식으로 주세요)', ReservationSerializer),
            400: openapi.Response('해당되는 스터디룸이 없거나 날짜&시간을 잘못 입력하였습니다.')
        }
      )
    @csrf_exempt  
    def get(self,request,room_name,date,clock):
        name=room_name
        date=date
        try:
            clock_value = Rclock.objects.get(time=clock)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        # clock_values를 Rclock 모델의 객체로 변환합니다.
        #clock_objects = [self.get_rclock_from_time_str(value) for value in clock_value]
        rstudy = Reservation.objects.filter(room__name=name, date=date, clocks__in=clock_values).first()
    
        if rstudy:
            serializers=ReservationSerializer(rstudy)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        return Response({"detail": "해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
class Reservationadmin(APIView):
    @swagger_auto_schema(
        responses = {
            201: openapi.Response('해당 스터디룸&날짜 예약현황 조회 성공(date는 2023-12-31형식으로 주세요)', ReservationSerializer),
            400: openapi.Response('해당되는 스터디룸이 없거나 날짜&시간을 잘못 입력하였습니다.')
        }
      )
    @csrf_exempt  
    def get(self,request,room_name,date):
        name=room_name
        date=date
        # clock_values를 Rclock 모델의 객체로 변환합니다.
        #clock_objects = [self.get_rclock_from_time_str(value) for value in clock_value]
        rstudy = Reservation.objects.filter(room__name=name, date=date)
    
        if rstudy:
            serializers=ReservationSerializer(rstudy,many=True )
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        return Response({"detail": "해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다."}, status=status.HTTP_400_BAD_REQUEST)    


#@permission_classes([IsAdminUser])    
class Reservationadmindelete(APIView):
    @swagger_auto_schema(
        responses = {
            201: openapi.Response('해당 스터디룸&날짜&시간의 예약현황 조회 성공(date는 2023-12-31,clock은 04:00pm 형식으로 주세요)', ReservationSerializer),
            400: openapi.Response('해당되는 스터디룸이 없거나 날짜&시간을 잘못 입력하였습니다.')
        }
      )
    @csrf_exempt  
    def get(self,request,room_name,date,clock):
        name=room_name
        date=date
        try:
            clock_value = Rclock.objects.get(time=clock)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        # clock_values를 Rclock 모델의 객체로 변환합니다.
        #clock_objects = [self.get_rclock_from_time_str(value) for value in clock_value]
        rstudy = Reservation.objects.filter(room__name=name, date=date, clocks__in=clock_values).first()
    
        if rstudy:
            serializers=ReservationSerializer(rstudy)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        return Response({"detail": "해당되는 스터디룸이 없거나 날짜를 잘못 입력하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response('예약 삭제 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
    
    @csrf_exempt      
    def delete(self,request,room_name, date,clock):
        name=room_name
        date=date
        try:
            clock_value = Rclock.objects.get(time=clock)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        delreservation = Reservation.objects.filter(room__name=name, date=date, clocks__in=clock_values).first()
        study_room = StudyRoom.objects.get(name=room_name, date=date)
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


##--------------로그인 유지 실패했을 때 코드들 --------------------------    

class MyReservation2(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('내 예약 목록 조회 성공(로그인 유지가 안될때 이거를 쓰세요)', ReservationSerializer(many=True)),
            204: openapi.Response('내 예약 목록이 없음' ),
            404: openapi.Response('사용자의 예약 정보를 찾을 수 없음'),
        }
    )
    @csrf_exempt  
    def get(self,request,schoolnumber):
        try:
            user=Profile.objects.get(schoolnumber=schoolnumber)
        except Profile.DoesNotExist:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
            
        if not user.is_authenticated:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)

        reservations=Reservation.objects.filter(user=user).order_by('-date')
        
        if not reservations:
            return Response({'message': '예약한 목록이 없습니다.'}, status=status.HTTP_204_NO_CONTENT)
        serializer=ReservationSerializer(reservations,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class ReservationAPIView2(APIView):
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
            400: openapi.Response('데이터 입력 오류'),
            401: openapi.Response('예약 실패(사유:이미 기존 예약이 있음)'),
            404: openapi.Response('사용자 정보를 찾을 수 없음'),
            406: openapi.Response('예약 실패(사유:하루 최대 2시간까지 예약 가능)'),
        }
    )
    @csrf_exempt    
    def post(self, request,schoolnumber):
        try:
            # 요청에서 필요한 데이터를 가져옵니다.
            room_name = request.data.get("room")
            date_str = request.data.get("date")
            clock_values = request.data.get("clock", [])     
            # 필수 필드(room, date, clock)가 누락되었는지 확인합니다.
            if not room_name or not date_str or not clock_values:
                return Response({"detail": "필수 필드 중 하나 이상이 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 날짜 형식 검증을 수행합니다.
            # 날짜 형식 검증을 수행합니다.
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"detail": "유효하지 않은 날짜 형식입니다."}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"detail": "해당 일자, 스터디룸, 시각에 이미 예약이 있습니다."}, status=status.HTTP_401_UNAUTHORIZED)

            # 유저가 해당 날짜에 이미 예약한 시간 수를 계산
            try:
                user = Profile.objects.get(schoolnumber=schoolnumber)  #로그인 유지 실패했을때
            except Profile.DoesNotExist:
                return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
            # 선택한 날짜에 대한 모든 예약을 가져옵니다.
            reservations_on_date = Reservation.objects.filter(user=user, date=date)
            total_clock_count = 0

            # 각 예약의 시간대 개수를 더합니다.
            for reservation in reservations_on_date:
                total_clock_count += reservation.clocks.count()
                        
            print(total_clock_count)
            # 하루 최대 2시간까지 예약 가능한지 확인합니다.
            if (total_clock_count +len(clock_values))> 4:
                return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)

            '''reservations_on_date = Reservation.objects.filter(user=user, date=date) \
                .annotate(clock_count=Count('clocks')) \
                .first()
            # 하루에 최대 2시간까지 예약할 수 있는지 확인하고 예약을 생성합니다.
            if reservations_on_date and reservations_on_date.clock_count >= 4:
                return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_401_UNAUTHORIZED)'''

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
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteReservation2(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('삭제할 에약 정보 조회 성공'),
            404: openapi.Response('삭제할 예약 정보가 없음'),
        }
    )
    @csrf_exempt  
    def get(self,request,schoolnumber,room_name, date,clock_value):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        try:
            user=Profile.objects.get(schoolnumber=schoolnumber)
        except Profile.DoesNotExist:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
        try:
            clock_value = Rclock.objects.get(time=clock_value)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        delreservation = Reservation.objects.filter(room__name=room_name, date=date, clocks__in=clock_values).first()
        #delreservation = get_object_or_404(Reservation, user=user, room=study_room)
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
    def delete(self,request,schoolnumber,room_name, date,clock_value):
        study_room = StudyRoom.objects.get(name=room_name, date=date)
        try:
            user=Profile.objects.get(schoolnumber=schoolnumber)
        except Profile.DoesNotExist:
            return Response({'message':'사용자 정보를 찾을 수 없습니다.'},status=status.HTTP_404_NOT_FOUND)
        
        try:
            clock_value = Rclock.objects.get(time=clock_value)
        except Rclock.DoesNotExist:
            return Response({"detail": "올바른 시간 형식이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
        clock_values=[clock_value]
        delreservation = Reservation.objects.filter(room__name=room_name, date=date, clocks__in=clock_values).first()
        
        #delreservation = get_object_or_404(Reservation, user=user, room=study_room)
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
    
    
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    
    # 뷰 로직을 이어서 처리하거나 HttpResponse 반환
    return HttpResponse('View executed successfully')
    
        
    
