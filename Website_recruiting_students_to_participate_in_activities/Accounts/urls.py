from django.urls import path
from Accounts.views import *

urlpatterns = [
    path('', home, name='home'),
    path('RegisterStudent/', RegisterStudent, name='RegisterStudent'),
    path('RegisterResponsible/', RegisterResponsible, name='RegisterResponsible'),
    path('RegisterFacultyStaff/', RegisterFacultyStaff, name='RegisterFacultyStaff'),

    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('Accounts/profile_Student', profile_Student, name='profile_Student'),
    path('Accounts/updateprofile_Student/<int:id>/', updateprofile_Student, name='updateprofile_Student'),
    path('Accounts/profile_Student_Credit/<int:id>/', profile_Student_Credit, name='profile_Student_Credit'),

    path('Accounts/profile_Responsible', profile_Responsible, name='profile_Responsible'),
    path('Accounts/updateprofile_Responsible/<int:id>/', updateprofile_Responsible, name='updateprofile_Responsible'),

    path('Accounts/profile_FacultyStaff', profile_FacultyStaff, name='profile_FacultyStaff'),
    path('Accounts/updateprofile_FacultyStaff/<int:id>/', updateprofile_FacultyStaff, name='updateprofile_FacultyStaff'),
]