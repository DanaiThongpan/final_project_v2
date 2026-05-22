from django.contrib import admin
from ActivityParticipationManagementSystem.models import *
# Register your models here.
class ActivityAdminDisplay(admin.ModelAdmin):
    list_display = ('announcement_date',
                    'semester',
                    'is_approved',
                    'img_activity', 
                    'activity_name', 
                    'activity_type', 
                    'due_date_registration',
                    'description', 
                    'credit')

admin.site.register(Activity, ActivityAdminDisplay)

class ActivityTimeEventAdminDisplay(admin.ModelAdmin):
    list_display = ('activity', 'start_date_activity', 'due_date_activity', 'place')

admin.site.register(ActivityTimeEvent, ActivityTimeEventAdminDisplay)

class ActivityParticipantAdminDisplay(admin.ModelAdmin):
    list_display = ('user_student', 'activity', 'is_approved')

admin.site.register(ActivityParticipant, ActivityParticipantAdminDisplay)

class ActivityPdfAdminDisplay(admin.ModelAdmin):
    list_display = ('activity', 'pdf_file')

admin.site.register(ActivityPdf, ActivityPdfAdminDisplay)