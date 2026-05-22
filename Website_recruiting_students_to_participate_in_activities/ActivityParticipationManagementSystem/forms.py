from django import forms
from ActivityParticipationManagementSystem.models import *
# Create your models here.
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            'img_activity',
            'academic_year',
            'semester',
            'activity_name',
            'activity_type',
            'due_date_registration',
            'max_participants',
            'description',
            'credit',
            'number_of_days',
        ]

        labels = {
            'img_activity' : 'รูปกิจกรรม ',
            'academic_year' : 'ปีการศึกษา ',
            'activity_name' : 'ชื่อกิจกรรม ',
            'activity_type' : 'ด้านที่ ',
            'due_date_registration' : 'เปิดให้ลงทะเบียนถึงวันที่',
            'max_participants' : 'จำนวนเป้าหมาย ',
            'semester' : 'เทอม ',
            'description' : 'คำอธิบาย ',
            'credit' : 'จำนวนหน่วยกิจกรรม',
            'number_of_days' : 'จำนวนวันที่จัดกิจกรรม',
        }

        widgets = {
            'due_date_registration': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'type': 'datetime-local'}),
        }

class ActivityTimeEventForm(forms.ModelForm):
    class Meta:
        model = ActivityTimeEvent
        fields = ['activity']  

        labels = {
            'activity' : 'id',
            'place' : 'สถานที่จัดกิจกรรม ',
            'start_date_activity' : 'วันที่จัดกิจกรรม ',
            'due_date_activity' : 'วันที่สิ้นสุดกิจกรรม ',
        }

        widgets = {
            'start_date_activity': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'type': 'datetime-local'}),
            'due_date_activity': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'type': 'datetime-local'}),
        }
        
    def __init__(self, *args, num_of_days=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_of_days = num_of_days

        self.fields['activity'].widget = forms.HiddenInput()  

        for i in range(self.num_of_days):
            self.fields[f'start_date_activity_{i}'] = forms.DateTimeField(
                label=f'วันที่เริ่มกิจกรรม (วันที่ {i+1})',
                required=True,
                widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'type': 'datetime-local'})
            )
            self.fields[f'due_date_activity_{i}'] = forms.DateTimeField(
                label=f'วันที่สิ้นสุดกิจกรรม (วันที่ {i+1})',
                required=True,
                widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'type': 'datetime-local'})
            )
            self.fields[f'place{i}'] = forms.CharField(
                label=f'สถานที่จัดกิจกรรม (วันที่ {i+1})',
                required=True
            )

class ActivityParticipantForm(forms.ModelForm):
    class Meta:
        model = ActivityParticipant
        fields = '__all__'

class ActivityPdfForm(forms.ModelForm):
    class Meta:
        model = ActivityPdf
        fields = ['pdf_file']