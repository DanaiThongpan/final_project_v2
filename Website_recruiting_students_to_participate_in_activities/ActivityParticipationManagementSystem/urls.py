from django.urls import path
from ActivityParticipationManagementSystem.views import *

urlpatterns = [
    path('homeStudent/', homeStudent, name='homeStudent'),
    path('homeStudent/activity_student/<int:id>/', activity_student, name='activity_student'),
    path('homeStudent/activity_student_history/', activity_student_history, name='activity_student_history'),
    
    path('homeResponsible', homeResponsible, name='homeResponsible'),
    path('create_activity_Responsible/', create_activity_Responsible, name='create_activity_Responsible'),
    path('create_activity_timeevent_Responsible/<int:activity_id>/', create_activity_timeevent_Responsible, name='create_activity_timeevent_Responsible'),
    path('update_activity_Responsible/<int:activity_id>/', update_activity_Responsible, name='update_activity_Responsible'),
    path('delete_activity_Responsible/<int:id>/', delete_activity_Responsible, name='delete_activity_Responsible'),
    path('homeResponsible/<int:activity_id>/upload_pdf_Responsible/', upload_pdf_Responsible, name='upload_pdf_Responsible'),
    path('homeResponsible/delete_pdf_Responsible/<int:pdf_id>/', delete_pdf_Responsible, name='delete_pdf_Responsible'),
    path('homeResponsible/<int:activity_id>/check_student_list_Responsible/', check_student_list_Responsible, name='check_student_list_Responsible'),
    path('generate_pdf_registration_form_Responsible/<int:id>/', generate_pdf_registration_form_Responsible, name='generate_pdf_registration_form_Responsible'),
    path('generate_pdf_sign_up_form_Responsible/<int:id>/', generate_pdf_sign_up_form_Responsible, name='generate_pdf_sign_up_form_Responsible'),
    path('dashboard_Responsible/', dashboard_Responsible, name='dashboard_Responsible'),

    path('homeFacultyStaff/', homeFacultyStaff, name='homeFacultyStaff'),
    path('home_activity_FacultyStaff/', home_activity_FacultyStaff, name='home_activity_FacultyStaff'),
    path('download_activity_csv_FacultyStaff/<int:activity_id>/', download_activity_csv_FacultyStaff, name='download_activity_csv_FacultyStaff'),
    path('create_activity_FacultyStaff/', create_activity_FacultyStaff, name='create_activity_FacultyStaff'),
    path('create_activity_timeevent_FacultyStaff/<int:activity_id>/', create_activity_timeevent_FacultyStaff, name='create_activity_timeevent_FacultyStaff'),
    path('home_activity_FacultyStaff/update_activity_FacultyStaff/<int:activity_id>/', update_activity_FacultyStaff, name='update_activity_FacultyStaff'),
    path('home_activity_FacultyStaff/delete_activity_FacultyStaff/<int:id>/', delete_activity_FacultyStaff, name='delete_activity_FacultyStaff'),
    path('home_activity_FacultyStaff/<int:activity_id>/check_student_list_FacultyStaff/', check_student_list_FacultyStaff, name='check_student_list_FacultyStaff'),
    path('homeFacultyStaff/<int:activity_id>/upload_pdf_FacultyStaff/', upload_pdf_FacultyStaff, name='upload_pdf_FacultyStaff'),
    path('home_activity_FacultyStaff/delete_pdf_FacultyStaff/<int:pdf_id>/', delete_pdf_FacultyStaff, name='delete_pdf_FacultyStaff'),
    path('home_activity_FacultyStaff/generate_pdf_registration_form_FacultyStaff/<int:id>/', generate_pdf_registration_form_FacultyStaff, name='generate_pdf_registration_form_FacultyStaff'),
    path('home_activity_FacultyStaff/generate_pdf_sign_up_form_FacultyStaff/<int:id>/', generate_pdf_sign_up_form_FacultyStaff, name='generate_pdf_sign_up_form_FacultyStaff'),
    path('dashboard_FacultyStaff/', dashboard_FacultyStaff, name='dashboard_FacultyStaff'),

    path('homAdmin/', homeAdmin, name='homeAdmin'),
    path('dashboard_Admin/', dashboard_Admin, name='dashboard_Admin'),

    path('dashboard_api/', dashboard_api, name='dashboard_api'),
]