# Create your models here.
from datetime import timedelta
from django.db import models
from Accounts.models import *
from django.utils import timezone  
from django.utils.timezone import now  

class ActivityManager(models.Manager):
    def close_expired_registrations(self):
        expired_activities = self.filter(due_date_registration__lt=timezone.now(), is_registration_open=True)
        for activity in expired_activities:
            activity.is_registration_open = False
            activity.save()

def upload_to_activity_img_activity(instance, filename):
    """
    สร้างโฟลเดอร์สำหรับการจัดเก็บไฟล์ PDF โดยแยกตาม:
    - ชื่อคณะ (faculty)
    - ชื่อผู้ใช้ (username)
    """
    if instance.user_faculty_staff:
        user_type = 'faculty_staff'
        faculty = instance.user_faculty_staff.faculty
        user_create = instance.user_faculty_staff.user.first_name
    elif instance.user_responsible:
        user_type = 'person_responsible'
        faculty = instance.user_responsible.faculty
        user_create = instance.user_responsible.user.first_name
    else:
        user_type = 'unknown_user'
        faculty = 'unknown_faculty'
        user_create = 'unknown_user'
    return os.path.join(f'activity_media/{user_type}/{faculty}/{user_create}/{instance.activity_name}', filename)

act_choices=[
        ('1 ด้านวิชาการที่ส่งเสริมคุณลักษณะบัณฑิตที่พึงประสงค์', '1 ด้านวิชาการที่ส่งเสริมคุณลักษณะบัณฑิตที่พึงประสงค์'),
        ('2 ด้านกีฬาหรือการส่งเสริมสุขภาพ', '2 ด้านกีฬาหรือการส่งเสริมสุขภาพ'),
        ('3 ด้านบำเพ็ญประโยชน์หรือรักษาสิ่งแวดล้อม', '3 ด้านบำเพ็ญประโยชน์หรือรักษาสิ่งแวดล้อม'),
        ('4 ด้านเสริมสร้างคุณธรรมและจริยธรรม', '4 ด้านเสริมสร้างคุณธรรมและจริยธรรม'),
        ('5 ด้านส่งเสริมศิลปะและวัฒนธรรม', '5 ด้านส่งเสริมศิลปะและวัฒนธรรม'),
        ('6 ด้านกิจกรรมอื่นๆ', '6 ด้านกิจกรรมอื่นๆ')]

class Activity(models.Model):
    user_faculty_staff = models.ForeignKey(UserFacultyStaff, null=True, blank=True, on_delete=models.CASCADE, related_name='create_activity_faculty')
    user_responsible = models.ForeignKey(UserResponsible, null=True, blank=True, on_delete=models.CASCADE, related_name='create_activity_responsible')
    img_activity = models.ImageField(upload_to=upload_to_activity_img_activity, blank=True, null=True)
    activity_name = models.CharField(max_length=30)
    activity_type = models.CharField(max_length=100, choices=act_choices)
    due_date_registration = models.DateTimeField()   
    description = models.CharField(max_length=30)
    credit = models.IntegerField(default=0)
    max_participants = models.IntegerField()
    registered_count = models.IntegerField(default=0)
    is_registration_open = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  
    announcement_date = models.DateTimeField(auto_now_add=True)
    number_of_days = models.IntegerField(default=1)
    SEMESTER_CHOICES = [
        ('1', '1'),
        ('2', '2')]
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, blank=True)
    academic_year = models.IntegerField(default=now().year + 543)
    objects = ActivityManager()
    def save(self, *args, **kwargs):
        current_year = now().year + 543
        SEMESTER_CHOICES = [
            (f'1', f'1'),
            (f'2', f'2'),
        ]
        self._meta.get_field('semester').choices = SEMESTER_CHOICES

        if not self.semester:
            self.semester = f'1/{current_year}'

        if self.registered_count >= self.max_participants or timezone.now() > self.due_date_registration:
            self.is_registration_open = False
        super().save(*args, **kwargs)

class ActivityTimeEvent(models.Model):
    activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.CASCADE, related_name='ActivityTimeEvent')
    place = models.CharField(max_length=30)
    start_date_activity = models.DateTimeField()
    due_date_activity = models.DateTimeField()

import os

def upload_to_activity_pdfs(instance, filename):
    user = instance.activity

    if user.user_faculty_staff:
        user_type = 'faculty_staff'
        faculty = user.user_faculty_staff.faculty
        user_create = user.user_faculty_staff.user.first_name
    elif user.user_responsible:
        user_type = 'person_responsible'
        faculty = user.user_responsible.faculty
        user_create = user.user_responsible.user.first_name
    else:
        user_type = 'unknown_user'

    return os.path.join(f'activity_media/{user_type}/{faculty}/{user_create}/{user.activity_name}', filename)

class ActivityPdf(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='ActivityPdf')
    pdf_file = models.FileField(upload_to=upload_to_activity_pdfs, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ActivityParticipant(models.Model):
    user_student = models.ForeignKey(UserStudent, on_delete=models.CASCADE, related_name='student_Participant')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_Participant')
    registered_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)   


