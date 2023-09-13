"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from geouser.views import *
from reserve.views import *
from django.views.static import serve
from django.conf import settings
from django.contrib.auth import views as auth_views


from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title = "공간정보 스터디룸 예약시스템 api",
        default_version = "v1",
        description = "Swagger를 사용한 '공간정보 스터디룸 예약시스템' API 문서(미완성)",
    ),
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/',SignupAPIView.as_view(),name='signup'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path('logout/',LogoutAPIView.as_view(),name='logout'),
    path('reservationadd/',ReservationAPIView.as_view(),name='reservation'),
    #path('create/', CreateStudyRooms.as_view(), name='create'),
    path('reservationtable/', ReservationTable.as_view(), name='reservationtable'),
    path('userlist/', MemberListAPIView.as_view(), name='member-list'),
    path('reservation/<int:pk>/',ReservationDetail.as_view(),name='reservationdatail'),
    path('reservationdelete/<int:pk>/',DeleteReservation.as_view(),name='reservationdelete'),
    path('myreservation/',MyReservation.as_view(),name='myservation'),
    path('reservationall/',ReservationListAPIView.as_view(),name='myservation'),
    
    
       # Swagger url
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
