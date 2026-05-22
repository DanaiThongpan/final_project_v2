from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from Accounts.models import *

#ผู้ใช้ทั้งหมด
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {'username': 'ชื่อผู้ใช้งาน','first_name': 'ชื่อ','last_name': 'นามสกุล','email': 'อีเมล'}

class StudentActivityYearForm(forms.ModelForm):
    class Meta:
        model = StudentYearlyActivityCredit
        fields = [
            'required_credits_category_1',
            'earned_credits_category_1',
            'required_credits_category_2',
            'earned_credits_category_2',
            'required_credits_category_3',
            'earned_credits_category_3',
            'required_credits_category_4',
            'earned_credits_category_4',
            'required_credits_category_5',
            'earned_credits_category_5',
            'required_credits_category_6',
            'earned_credits_category_6']
        
        labels = {
            'required_credits_category_1': 'ด้านที่ 1: ต้องการ', 
            'earned_credits_category_1': 'ด้านที่ 1: ที่มี',
            'required_credits_category_2': 'ด้านที่ 2: ต้องการ', 
            'earned_credits_category_2': 'ด้านที่ 2: ที่มี',
            'required_credits_category_3': 'ด้านที่ 3: ต้องการ', 
            'earned_credits_category_3': 'ด้านที่ 3: ที่มี',
            'required_credits_category_4': 'ด้านที่ 4: ต้องการ', 
            'earned_credits_category_4': 'ด้านที่ 4: ที่มี',
            'required_credits_category_5': 'ด้านที่ 5: ต้องการ', 
            'earned_credits_category_5': 'ด้านที่ 5: ที่มี',
            'required_credits_category_6': 'ด้านที่ 6: ต้องการ', 
            'earned_credits_category_6': 'ด้านที่ 6: ที่มี'}

class UserStudentForm(forms.ModelForm):
    class Meta:
        model = UserStudent
        fields = ['title', 
                  'faculty',
                  'type_scholarship',
                  'years_of_study',
                  'current_year',
                  ]
        labels = {'title' : 'คำนำหน้า', 
                  'faculty' : 'คณะ', 
                  'years_of_study' : 'จำนวนปีของหลักสูตร', 
                  'current_year' : 'ปีที่กำลังศึกษาอยู่', 
                  'type_scholarship' : 'ประเภท(ทุน-กยศ)'}
        
class UserStudentUpdateForm(forms.ModelForm):
    class Meta:
        model = UserStudent
        fields = ['title', 'faculty', 
                  'type_scholarship',
                  'years_of_study',
                  'current_year']
        labels = {'title' : 'คำนำหน้า', 
                  'faculty' : 'คณะ', 
                  'years_of_study' : 'จำนวนปีของหลักสูตร', 
                  'current_year' : 'ปีที่กำลังศึกษาอยู่', 
                  'type_scholarship' : 'ประเภท(ทุน-กยศ)'}
        
class UserResponsibleForm(forms.ModelForm):
    class Meta:
        model = UserResponsible
        fields = ['title', 'faculty']
        labels = {'title' : 'คำนำหน้า', 'faculty' : 'คณะ'}
    
class UserResponsibleUpdateForm(forms.ModelForm):
    class Meta:
        model = UserResponsible
        fields = ['title', 'faculty']
        labels = {'title': 'คำนำหน้า', 'faculty': 'คณะ'}
        
class UserFacultyStaffForm(forms.ModelForm):
    class Meta:
        model = UserFacultyStaff
        fields = ['title', 'faculty']
        labels = {'title' : 'คำนำหน้า', 'faculty' : 'คณะ'}

class UserFacultyStaffUpdateForm(forms.ModelForm):
    class Meta:
        model = UserFacultyStaff
        fields = ['title', 'faculty']
        labels = {'title' : 'คำนำหน้า', 'faculty' : 'คณะ'}