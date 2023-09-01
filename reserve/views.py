from django.db.models import Count
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reservation, Rclock, StudyRoom

# Create your views here.

class ReservationAPIView(APIView):
    def post(self, request):
        user = request.user
        room_name = request.data.get("room")
        date = request.data.get("date")
        clocks_values = request.data.get("clocks", [])[:2]

        try:
            room = StudyRoom.objects.get(name=room_name)
        except StudyRoom.DoesNotExist:
            return Response({"detail": "해당 스터디룸이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 이미 해당 일자, 스터디룸, 시각에 예약이 있는지 확인
        existing_reservation = Reservation.objects.filter(
            room=room,
            date=date,
            clocks__time__in=clocks_values
        ).first()

        if existing_reservation:
            return Response({"detail": "해당 일자, 스터디룸, 시각에 이미 예약이 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 유저가 해당 날짜에 이미 예약한 시간 수를 계산
        reservations_on_date = Reservation.objects.filter(user=user, date=date) \
            .annotate(clock_count=Count('clock')) \
            .first()

        if reservations_on_date and reservations_on_date.clocks_count >= 2:
            return Response({"detail": "하루에 최대 2시간까지 예약할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 'clock' 값을 최대 2개까지 저장
        reserve = Reservation(user=user, room=room, date=date)
        reserve.save()

        for value in clocks_values:
            rclock, created = Rclock.objects.get_or_create(time=value)
            reserve.clocks.add(rclock)

        return Response({"detail": "성공적으로 예약하였습니다."}, status=status.HTTP_201_CREATED)
