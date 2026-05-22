# Create your models here.
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

title__choices = [('นาย', 'นาย'), ('นางสาว', 'นางสาว'), ('นาง', 'นาง')]
faculty_choices = [ ('วิทยาศาสตร์', 'วิทยาศาสตร์'), ('คณะเกษตรศาสตร์', 'คณะเกษตรศาสตร์'), ('คณะวิศวกรรมศาสตร์', 'คณะวิศวกรรมศาสตร์'), ('คณะศิลปศาสตร์', 'คณะศิลปศาสตร์'), ('คณะเภสัชศาสตร์', 'คณะเภสัชศาสตร์'), ('คณะบริหารศาสตร์', 'คณะบริหารศาสตร์'), ('วิทยาลัยแพทยศาสตร์และการสาธารณสุข', 'วิทยาลัยแพทยศาสตร์และการสาธารณสุข'), ('คณะนิติศาสตร์', 'คณะนิติศาสตร์'), ('คณะรัฐศาสตร์', 'คณะรัฐศาสตร์'), ('คณะพยาบาลศาสตร์', 'คณะพยาบาลศาสตร์')]
type_scholarship_choices = [('ทุน', 'ทุน'),('กยศ', 'กยศ'),('ทุน, กยศ', 'ทุน, กยศ')]

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_responsible = models.BooleanField(default=False)
    is_faculty_staff = models.BooleanField(default=False)
    
class UserStudent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserStudent')
    title = models.CharField(max_length=10, choices=title__choices, default="นาย")
    faculty = models.CharField(max_length=50, choices=faculty_choices, default="วิทยาศาสตร์")
    type_scholarship = models.CharField(max_length=50, choices=type_scholarship_choices)
    years_of_study = models.IntegerField(default=4) 
    current_year = models.IntegerField(default=1)

class UserResponsible(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserResponsible')
    title = models.CharField(max_length=10, choices=title__choices, default="นาย")
    faculty = models.CharField(max_length=50, choices=faculty_choices, default="วิทยาศาสตร์")
    
class UserFacultyStaff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UserFacultyStaff')
    title = models.CharField(max_length=10, choices=title__choices, default="นาย")
    faculty = models.CharField(max_length=50, choices=faculty_choices, default="วิทยาศาสตร์")
    is_approved = models.BooleanField(default=False)

def get_current_thai_year():
    """ฟังก์ชันสำหรับหาปี พ.ศ. ปัจจุบัน"""
    return date.today().year + 543

class StudentYearlyActivityCredit(models.Model):
    student = models.ForeignKey(UserStudent, on_delete=models.CASCADE, related_name='StudentYearlyActivityCredit')
    academic_year = models.IntegerField(default=get_current_thai_year, verbose_name="ปีการศึกษา (พ.ศ.)")
    year_level = models.IntegerField(default=1, verbose_name="ชั้นปีที่")
    required_credits_category_1 = models.FloatField(default=0, verbose_name="ด้าน 1 ต้องการ")
    required_credits_category_2 = models.FloatField(default=0, verbose_name="ด้าน 2 ต้องการ")
    required_credits_category_3 = models.FloatField(default=0, verbose_name="ด้าน 3 ต้องการ")
    required_credits_category_4 = models.FloatField(default=0, verbose_name="ด้าน 4 ต้องการ")
    required_credits_category_5 = models.FloatField(default=0, verbose_name="ด้าน 5 ต้องการ")
    required_credits_category_6 = models.FloatField(default=0, verbose_name="ด้าน 6 ต้องการ")
    earned_credits_category_1 = models.FloatField(default=0, verbose_name="ด้าน 1 มี")
    earned_credits_category_2 = models.FloatField(default=0, verbose_name="ด้าน 2 มี")
    earned_credits_category_3 = models.FloatField(default=0, verbose_name="ด้าน 3 มี")
    earned_credits_category_4 = models.FloatField(default=0, verbose_name="ด้าน 4 มี")
    earned_credits_category_5 = models.FloatField(default=0, verbose_name="ด้าน 5 มี")
    earned_credits_category_6 = models.FloatField(default=0, verbose_name="ด้าน 6 มี")

