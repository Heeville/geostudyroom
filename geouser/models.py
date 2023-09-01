from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# Create your models here.

class ProfileManager(BaseUserManager):
    def create_user(self, schoolnumber, password=None, **extra_fields):
        if not schoolnumber:
            raise ValueError('The User ID must be set')
        extra_fields.setdefault('password', make_password(password))  # 비밀번호 암호화
        user = self.model(schoolnumber=schoolnumber, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, schoolnumber, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(schoolnumber, password, **extra_fields)

class Profile(AbstractBaseUser):
    schoolnumber=models.CharField(max_length=10,unique=True)
    name = models.CharField(max_length=10)
    password = models.CharField(max_length=120)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'schoolnumber'
    
    objects = ProfileManager() 
    
    def __str__(self):
        return f"{self.schoolnumber} {self.name}"
    
    def has_perm(self, perm, obj=None):
        # 필요한 경우 권한 체크 로직을 구현합니다.
        # 예를 들어, 특정 권한을 가진 사용자인지 확인하는 로직을 작성합니다.
        return True  # 예시로 모든 사용자에게 권한을 부여함

    def has_perms(self, perm_list, obj=None):
        # 필요한 경우 다중 권한 체크 로직을 구현합니다.
        # 예를 들어, 여러 개의 권한 중 하나라도 가지고 있는지 확인하는 로직을 작성합니다.
        return True  # 예시로 모든 사용자에게 권한을 부여함
    
    def has_module_perms(self, app_label):
        return self.is_staff
