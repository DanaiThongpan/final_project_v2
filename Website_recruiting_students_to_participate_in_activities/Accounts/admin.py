from django.contrib import admin

# Register your models here.
from django.contrib import admin
from Accounts.models import *

# Register your models here.
class UserDisplay(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_responsible','is_faculty_staff']

admin.site.register(User, UserDisplay)

class UserStudentAdminDisplay(admin.ModelAdmin):
    list_display = ['user', 'title', 'faculty', 'type_scholarship', 'years_of_study','current_year',]

admin.site.register(UserStudent, UserStudentAdminDisplay)

class StudentActivityYearAdminDisplay(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'year_level']

admin.site.register(StudentYearlyActivityCredit, StudentActivityYearAdminDisplay)

class UserResponsibleAdminDisplay(admin.ModelAdmin):
    list_display = ['user', 'title', 'faculty']

admin.site.register(UserResponsible, UserResponsibleAdminDisplay)

class UserUserFacultyStaffAdminDisplay(admin.ModelAdmin):
    list_display = ['user','title', 'faculty','is_approved']

admin.site.register(UserFacultyStaff, UserUserFacultyStaffAdminDisplay)