import base64
import csv
from pyexpat.errors import messages
from django.forms import ValidationError
from django.db import transaction
from django.shortcuts import *
from Accounts.forms import *
from ActivityParticipationManagementSystem.models import *
from ActivityParticipationManagementSystem.forms import *
from django.contrib.auth.decorators import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
import os
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from django.utils.encoding import iri_to_uri  
# Create your views here.
#####################################################################################
def is_student(user):
    return user.is_authenticated and hasattr(user, 'is_student') and user.is_student

@login_required
@user_passes_test(is_student, login_url='login')
def homeStudent(request):
    user_student = UserStudent.objects.get(user=request.user)
    activity_student = Activity.objects.all()
    
    return render(request, 'Student/homeStudent.html', {
        'user_student' : user_student,
        'activity_student': activity_student,
        'act_choices': act_choices[:],
    })

@login_required
@user_passes_test(is_student, login_url='login')
def activity_student(request, id):
    activity_student_get_id = get_object_or_404(Activity, pk=id)
    user_student = get_object_or_404(UserStudent, user=request.user)
    existing_registration = ActivityParticipant.objects.filter(activity=activity_student_get_id, user_student=user_student).first()
    registered_students = ActivityParticipant.objects.filter(activity=activity_student_get_id).select_related('user_student')
    time_events = ActivityTimeEvent.objects.filter(activity_id=activity_student_get_id)

    def save_registration():
        if not activity_student_get_id.is_registration_open:
            raise ValidationError('Registration is closed for this activity.')  
        
        with transaction.atomic():
            if activity_student_get_id.registered_count < activity_student_get_id.max_participants:
                activity_student_get_id.registered_count += 1
                activity_student_get_id.save()
                ActivityParticipant.objects.create(user_student=user_student, activity=activity_student_get_id)
            else:
                raise ValidationError('No more slots available for this activity.')

    def cancel_registration():
        with transaction.atomic():
            if activity_student_get_id.registered_count > 0:
                activity_student_get_id.registered_count -= 1
                activity_student_get_id.is_registration_open = True
                activity_student_get_id.save()
            existing_registration.delete()

    if request.method == 'POST':
        if existing_registration:
            cancel_registration()
        else:
            save_registration()

        return redirect('activity_student', id=id)

    return render(request, 'Student/activity_student.html', {
        'user_student' : user_student,
        'activity_student_get_id': activity_student_get_id,
        'existing_registration': existing_registration,
        'registered_students': registered_students,
        'time_events': time_events,
    })

@login_required
@user_passes_test(is_student, login_url='login')
def activity_student_history(request):
    user_student = get_object_or_404(UserStudent, user=request.user)
    user = request.user
    activity_student_history = ActivityParticipant.objects.filter(user_student=user_student).select_related('activity')

    return render(request, 'Student/activity_student_history.html', {
        'user_student' : user_student,
        'activity_student_history' : activity_student_history,
        'act_choices': act_choices[:],
    })

#####################################################################################
def is_responsible(user):
    return user.is_authenticated and hasattr(user, 'is_responsible') and user.is_responsible

@login_required
@user_passes_test(is_responsible, login_url='login')
def homeResponsible(request):
    user_responsible = get_object_or_404(UserResponsible, user=request.user)
    activity_type = request.GET.get('activity_type', 'all')

    if activity_type == 'all':
        activitys_responsible = Activity.objects.filter(
            Q(user_responsible=user_responsible)  
        )
    else:
        activitys_responsible = Activity.objects.filter(
            Q(user_responsible=user_responsible),
            activity_type=activity_type  
        )

    return render(request, 'Responsible/homeResponsible.html', {
        'user_responsible' : user_responsible,
        'activitys_responsible': activitys_responsible,
        'act_choices': act_choices[:],
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def create_activity_Responsible(request):
    user_responsible = UserResponsible.objects.get(user=request.user)
    activity_form = ActivityForm()
    if request.method == 'POST':
        activity_form = ActivityForm(request.POST, request.FILES)
        if activity_form.is_valid():
            activity = activity_form.save(commit=False)
            activity.user_responsible = user_responsible
            activity.save()
            return redirect('create_activity_timeevent_Responsible', activity_id=activity.id)
    
    return render(request, 'Responsible/create_activity_Responsible.html', {
        'user_responsible' : user_responsible,
        'activity_form' : activity_form
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def create_activity_timeevent_Responsible(request, activity_id):
    user_responsible = get_object_or_404(UserResponsible, user=request.user)
    activitys_responsible = get_object_or_404(Activity, id=activity_id)
    num_of_days = activitys_responsible.number_of_days

    if request.method == 'POST':
        activity_timeevent_Form = ActivityTimeEventForm(request.POST, request.FILES, num_of_days=num_of_days)
        if activity_timeevent_Form.is_valid():
            for i in range(num_of_days):
                time_event = ActivityTimeEvent(
                    activity=activitys_responsible,
                    start_date_activity=activity_timeevent_Form.cleaned_data[f'start_date_activity_{i}'],
                    due_date_activity=activity_timeevent_Form.cleaned_data[f'due_date_activity_{i}'],
                    place=activity_timeevent_Form.cleaned_data[f'place{i}']
                )
                time_event.save()
            return redirect('homeResponsible')
    else:
        activity_timeevent_Form = ActivityTimeEventForm(num_of_days=num_of_days)

    return render(request, 'Responsible/create_activity_timeevent_Responsible.html', {
        'activity_timeevent_Form': activity_timeevent_Form,
        'activitys_responsible': activitys_responsible,
        'user_responsible' : user_responsible,
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def update_activity_Responsible(request, activity_id):
    user_responsible = get_object_or_404(UserResponsible, user=request.user)
    activitys_responsible = Activity.objects.get(pk=activity_id)
    activity_form = ActivityForm(instance=activitys_responsible)
    
    if request.method == 'POST':
        activity_form = ActivityForm(request.POST, request.FILES, instance=activitys_responsible)
        
        if activity_form.is_valid():
            activity = activity_form.save(commit=False)

            if activity.due_date_registration >= timezone.now():
                activity.is_registration_open = True
            else:
                activity.is_registration_open = False

            activity.save()  
            
            return redirect('homeResponsible')
    
    return render(request, 'Responsible/update_activity_Responsible.html', {
        'activity_form': activity_form,
        'activitys_responsible': activitys_responsible,
        'user_responsible' : user_responsible,
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def delete_activity_Responsible(request, id):
    activitys_responsible = get_object_or_404(Activity, pk=id)
    user_responsible = UserResponsible.objects.get(user=request.user)
    if activitys_responsible.user_responsible != user_responsible:
        return redirect('homeResponsible')
    else:
        activitys_responsible.delete()

    return redirect('homeResponsible')

@login_required
@user_passes_test(is_responsible, login_url='login')
def check_student_list_Responsible(request, activity_id):
    user_responsible = get_object_or_404(UserResponsible, user=request.user)
    activitys_responsible = get_object_or_404(Activity, id=activity_id)
    students_in_activity = ActivityParticipant.objects.filter(activity=activitys_responsible).select_related('user_student')

    if request.method == 'POST':
        selected_students = request.POST.getlist('student')
        
        for student_in_activity in students_in_activity:
            if str(student_in_activity.user_student.id) in selected_students:
                student_in_activity.is_approved = True
            else:
                student_in_activity.is_approved = False
            
            student_in_activity.save(update_fields=['is_approved'])

        return redirect('homeResponsible')
    
    return render(request, 'Responsible/check_student_list_Responsible.html', {
        'activitys_responsible': activitys_responsible,
        'students_in_activity': students_in_activity,
        'user_responsible' : user_responsible,
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def upload_pdf_Responsible(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    if ActivityPdf.objects.filter(activity=activity).exists():
        return redirect('homeResponsible')

    if request.method == 'POST':
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            ActivityPdf.objects.create(activity=activity, pdf_file=pdf_file)
            return redirect('homeResponsible')
        else:
            return redirect('homeResponsible')

    return render(request, 'Responsible/homeResponsible.html')

@login_required
@user_passes_test(is_responsible, login_url='login')
def delete_pdf_Responsible(request, pdf_id):
    pdf = get_object_or_404(ActivityPdf, id=pdf_id)
    pdf.pdf_file.delete()
    pdf.delete()
    
    return redirect('homeResponsible')

@login_required
@user_passes_test(is_responsible, login_url='login')
def generate_pdf_sign_up_form_Responsible(request, id):
    db_user = ActivityParticipant.objects.filter(activity_id=id)
    time_events = ActivityTimeEvent.objects.filter(activity_id=id)  
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    if db_user.exists():
        pdf.title = ('แบบบันทึกการเข้าร่วมกิจกรรม ' + db_user.first().activity.activity_name)
    else:
        pdf.title = 'แบบบันทึกการเข้าร่วมกิจกรรม'

    story = []
    font_path = os.path.join(settings.BASE_DIR, 'ActivityParticipationManagementSystem', 'path_to_fonts', 'THSarabunNew.ttf')

    if not os.path.exists(font_path):
        return HttpResponse(f"Font file not found at {font_path}", status=404)

    pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ThaiStyle', fontName='THSarabunNew', fontSize=16, leading=20))
    styles.add(ParagraphStyle(name='TableHeaderStyle', fontName='THSarabunNew', fontSize=14, alignment=1))
    styles.add(ParagraphStyle(name='TableCellStyle', fontName='THSarabunNew', fontSize=14, alignment=0))
    styles.add(ParagraphStyle(name='CenteredStyle', fontName='THSarabunNew', fontSize=16, alignment=1))

    if db_user.exists():
        activity_name = db_user.first().activity.activity_name
        for time_event in time_events:
            start_date_activity_thai = timezone.localtime(time_event.start_date_activity)
            due_date_activity_thai = timezone.localtime(time_event.due_date_activity)
            story.append(Paragraph(f"รายชื่อผู้เข้าร่วมกิจกรรม {activity_name}", styles['CenteredStyle']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"สถานที่: {time_event.place}", styles['CenteredStyle']))
            story.append(Paragraph(f"วันที่: {start_date_activity_thai.strftime('%d/%m/%Y')}", styles['CenteredStyle']))
            story.append(Paragraph(f"เวลา: {start_date_activity_thai.strftime('%H:%M')} - {due_date_activity_thai.strftime('%H:%M')}", styles['CenteredStyle']))
            story.append(Spacer(1, 12))
            data = [['ลำดับ', 'ชื่อ-สกุล', 'รหัสนักศึกษา', 'คณะ', 'ลงชื่อ']]
            for index, user in enumerate(db_user, start=1):
                full_name = f"{user.user_student.title} {user.user_student.user.first_name} {user.user_student.user.last_name}"
                student_id = user.user_student.user.username
                faculty = user.user_student.faculty
                data.append([str(index), full_name, student_id, faculty, ""])

            table = Table(data, colWidths=[50, 150, 100, 100, 100])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),
                ('FONTSIZE', (0, 0), (-1, 0), 16),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
            story.append(table)
            story.append(Spacer(1, 24)) 
            story.append(PageBreak())
    else:
        story.append(Paragraph("ไม่พบข้อมูลผู้เข้าร่วมกิจกรรม", styles['CenteredStyle']))

    pdf.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

    return render(request, 'Responsible/generate_pdf_sign_up_form_Responsible.html', {'pdf_base64': pdf_base64, 'activity_id': id})

@login_required
@user_passes_test(is_responsible, login_url='login')
def generate_pdf_registration_form_Responsible(request, id):
    activityparticipant = ActivityParticipant.objects.filter(activity_id=id)
    activitytimeEvent = ActivityTimeEvent.objects.filter(activity_id=id)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    font_path = os.path.join(settings.BASE_DIR, 'ActivityParticipationManagementSystem', 'path_to_fonts', 'THSarabunNew.ttf')
    pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))
    pdf.setFont("THSarabunNew", 14)
    pdf.setTitle('แบบบันทึกการเข้าร่วมกิจกรรม ' + activityparticipant.first().activity.activity_name)
    pdf.drawCentredString(10.5 * cm, 28.5 * cm, "แบบบันทึกการเข้าร่วมกิจกรรมของนักศึกษามหาวิทยาลัยอุบลราชธานี")
    pdf.drawString(2 * cm, 27.5 * cm, "ชื่อกิจกรรม (ภาษาไทย) _________________________________________________________________________________")
    pdf.drawString(6.5 * cm, 27.5 * cm, activityparticipant.first().activity.activity_name)
    pdf.drawString(2 * cm, 26.7 * cm, "ชื่อกิจกรรม (ภาษาอังกฤษ) _______________________________________________________________________________")  # ลดช่องไฟลงเล็กน้อย
    pdf.drawString(6.5 * cm, 26.7 * cm, "")
    pdf.drawString(2 * cm, 25.9 * cm, "หน่วยงานที่จัดกิจกรรม")  
    pdf.rect(7 * cm, 25.7 * cm, 0.4 * cm, 0.4 * cm)   
    pdf.drawString(7.5 * cm, 25.8 * cm, "หน่วยงานภายใน")
    pdf.line(7.1 * cm, 25.8 * cm, 7.3 * cm, 26 * cm)
    pdf.rect(12 * cm, 25.7 * cm, 0.4 * cm, 0.4 * cm)  
    pdf.drawString(12.5 * cm, 25.8 * cm, "หน่วยงานภายนอก")
    pdf.drawString(7 * cm, 25.1 * cm, "โปรดระบุชื่อหน่วยงาน _____________________________________________________")
    pdf.drawString(11 * cm, 25.3 * cm, "")
    pdf.drawString(2 * cm, 24.3 * cm, "ด้านกิจกรรม")  
    pdf.rect(4 * cm, 24.1 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 24.3 * cm, "วิชาการที่ส่งเสริมคุณลักษณะบัณฑิต")
    pdf.drawString(5 * cm, 23.8 * cm, "ที่พึงประสงค์")
    pdf.rect(4 * cm, 23.3 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 23.3 * cm, "กีฬา หรือการส่งเสริมสุขภาพ")
    pdf.rect(4 * cm, 22.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 22.5 * cm, "บำเพ็ญประโยชน์ หรือรักษาสิ่งแวดล้อม")
    pdf.rect(4 * cm, 21.7 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 21.7 * cm, "เสริมสร้างคุณธรรม และจริยธรรม")
    pdf.rect(4 * cm, 20.9* cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 20.9 * cm, "ส่งเสริมศิลปะ และวัฒนธรรม")
    pdf.rect(14 * cm, 24.1 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(12 * cm, 24.3 * cm, "ด้านกิจกรรม")
    pdf.drawString(12 * cm, 23.8 * cm, "ตาม TQF")
    pdf.drawString(15 * cm, 24.3 * cm, "ด้านคุณธรรมจริยธรรม")
    pdf.rect(14 * cm, 23.3 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 23.5 * cm, "ด้านความรู้")
    pdf.rect(14 * cm, 22.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 22.7 * cm, "ด้านทักษะทางปัญญา")
    pdf.rect(14 * cm, 21.7 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 21.9 * cm, "ด้านความสัมพันธ์ระหว่างบุคคล")
    pdf.drawString(15 * cm, 21.4 * cm, "ความรับผิดชอบ")
    pdf.rect(14 * cm, 20.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 20.5 * cm, "ด้านการวิเคราะห์เชิงตัวเลข การสื่อสาร")
    pdf.drawString(15 * cm, 20.0 * cm, "และการใช้เทคโนโลยี สารสนเทศ")
    pdf.drawString(2 * cm, 19.5 * cm, "จำนวนชั่วโมงที่เข้าร่วมกิจกรรม ________________") 
    hours = activityparticipant.first().activity.credit * 3
    pdf.drawString(7.5 * cm, 19.5 * cm, str(hours))
    pdf.drawString(9 * cm, 19.5 * cm, "ชั่วโมง")
    pdf.drawString(12 * cm, 19.5 * cm, "จำนวนผู้เข้าร่วม (เป้าหมาย) ______________")
    pdf.drawString(17 * cm, 19.5 * cm, str(activityparticipant.first().activity.max_participants))
    pdf.drawString(18.2 * cm, 19.5 * cm, "คน")
    pdf.drawString(2 * cm, 18.5 * cm, "วันที่เริ่ม ________________")
    pdf.drawString(6 * cm, 18.5 * cm, "เวลา ________________________")
    pdf.drawString(11 * cm, 18.5 * cm, "วันที่สิ้นสุด __________________")
    pdf.drawString(15.7 * cm, 18.5 * cm, "เวลา ____________________")
    responsible_person_t = activityparticipant.first().activity.user_responsible.title
    responsible_person_f = activityparticipant.first().activity.user_responsible.user.first_name
    responsible_person_l = activityparticipant.first().activity.user_responsible.user.last_name
    pdf.drawString(2 * cm, 17.5 * cm, "ผู้รับผิดชอบโครงการ ___________________________________")
    pdf.drawString(5 * cm, 17.5 * cm, responsible_person_t)
    pdf.drawString(6 * cm, 17.5 * cm, responsible_person_f)
    pdf.drawString(9 * cm, 17.5 * cm, responsible_person_l)
    pdf.drawString(11 * cm, 17.5 * cm, "ที่ปรึกษาโครงการ ______________________________________")
    pdf.drawString(5 * cm, 16.7 * cm, str(activitytimeEvent.first().place))
    pdf.drawString(2 * cm, 16.7 * cm, "สถานที่จัดกิจกรรม _________________________________________________________________________________________")
    pdf.drawString(5.5 * cm, 16.5 * cm, "")
    pdf.drawString(2 * cm, 16 * cm, "งบประมาณ")
    pdf.rect(4 * cm, 15.8 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 15.8 * cm, "เงินงบประมาณแผ่นดิน _____________________________")
    pdf.drawString(13 * cm, 15.8 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 15.8 * cm, "บาท")
    pdf.rect(4 * cm, 15 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 15 * cm, "เงินรายได้มหาวิทยาลัย _____________________________")
    pdf.drawString(13 * cm, 15 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 15 * cm, "บาท")
    pdf.rect(4 * cm, 14.2 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 14.2 * cm, "เงินรายได้อื่นๆ (โปรดระบุ) __________________________")
    pdf.drawString(13 * cm, 14.2 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 14.2 * cm, "บาท")
    pdf.drawString(2 * cm, 13.5 * cm, "คำอธิบายเกี่ยวกับ")
    pdf.drawString(2 * cm, 13.1 * cm, "กิจกรรม")
    pdf.drawString(6 * cm, 13.1 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 12.4 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 11.7 * cm, "________________________________________________________________________________")
    pdf.drawString(2 * cm, 11.5 * cm, "รายชื่อนักศึกษาที่เข้าร่วม")
    pdf.drawString(2 * cm, 11 * cm, "(กรุณาระบุ ชื่อ-สกุล คณะ")
    pdf.drawString(2 * cm, 10.5 * cm, "รหัสนักศึกษา หมายเลขติดต่อ")
    pdf.drawString(2 * cm, 10 * cm, "ให้ครบถ้วน)")
    pdf.drawString(6 * cm, 11 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 10.3 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 9.6 * cm, "________________________________________________________________________________")
    pdf.drawString(5 * cm, 9 * cm, "หมายเหตุ : โปรดแนบหลักฐานการเข้าร่วมกิจกรรม เช่น สําเนาโครงการ หนังสือเชิญ กําหนดการ รูปถ่าย เป็นต้น")
    pdf.drawString(6.4 * cm, 8.5 * cm, ": กรณีมีจํานวนนักศึกษาที่เข้าร่วมจํานวนมาก ให้แนบรายชื่อนักศึกษาพร้อมแบบบันทึกและชื่อรับรองทุกแผ่น")
    pdf.drawString(4 * cm, 7.5 * cm, "ข้าพเจ้าขอรับรองว่าให้เข้าร่วมกิจกรรม ตามวัน เวลา และสถานที่ที่กล่าวจริง จึงเรียบมาเพื่อโปรดพิจารณา")
    pdf.drawString(4 * cm, 6.5 * cm, "(ลงชื่อ) _________________")
    pdf.drawString(8 * cm, 6.5 * cm, "ผู้ยื่นคำร้อง")
    pdf.drawString(12 * cm, 6.5 * cm, "(ลงชื่อ) ___________________ ผู้รับรองกิจกรรม")
    pdf.drawString(4.8 * cm, 6 * cm, "( __________________ )")
    pdf.drawString(12.8 * cm, 6 * cm, "( ___________________ )")
    pdf.drawString(4.2 * cm, 5.5 * cm, "วันที่ ___________________")
    pdf.drawString(12.2 * cm, 5.5 * cm, "วันที่ ____________________")
    pdf.rect(2 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.rect(8 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.rect(14 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.drawString(2.5 * cm, 3.5 * cm, "(ลงชื่อ) _____________________")
    pdf.drawString(3 * cm, 3 * cm, "( _______________________ )")
    pdf.drawString(4 * cm, 2.4 * cm, "ผู้ตรวจสอบข้อมูล")
    pdf.drawString(2.5 * cm, 1.5 * cm, "วันที่ _______________________")
    pdf.drawString(8.2 * cm, 3.5 * cm, "คณะกรรมการพิจารณาแล้วเห็นสมควร")
    pdf.drawString(8.2 * cm, 3 * cm, "อนุมัติให้ค่าหน่วยกิจกรรมดังกล่าว")
    pdf.drawString(10.5 * cm, 2.4 * cm, str(activityparticipant.first().activity.credit))
    pdf.drawString(8.3 * cm, 2.4 * cm, "จำนวน _____________ หน่วยกิจกรรม")
    pdf.drawString(16.5 * cm, 4.3 * cm, "อนุมัติ")
    pdf.drawString(14.7 * cm, 3.5 * cm, "____________________________")
    pdf.drawString(14.5 * cm, 3 * cm, "( ____________________________ )")
    pdf.drawString(14.5 * cm, 1.5 * cm, "วันที่ _______________________")
    pdf.showPage()
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

    return render(request, 'Responsible/generate_pdf_registration_form_Responsible.html', {
        'pdf_base64': pdf_base64, 
        'activity_id': id
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def dashboard_Responsible(request):
    user_responsible = get_object_or_404(UserResponsible, user=request.user)

    return render(request, 'Responsible/dashboard_Responsible.html', {
        'user_responsible' : user_responsible
    })
#####################################################################################
def is_faculty_staff(user):
    return user.is_authenticated and hasattr(user, 'is_faculty_staff') and user.is_faculty_staff

CREDIT_FIELD_MAPPING = {
    '1 ด้านวิชาการที่ส่งเสริมคุณลักษณะบัณฑิตที่พึงประสงค์': 'earned_credits_category_1',
    '2 ด้านกีฬาหรือการส่งเสริมสุขภาพ': 'earned_credits_category_2',
    '3 ด้านบำเพ็ญประโยชน์หรือรักษาสิ่งแวดล้อม': 'earned_credits_category_3',
    '4 ด้านเสริมสร้างคุณธรรมและจริยธรรม': 'earned_credits_category_4',
    '5 ด้านส่งเสริมศิลปะและวัฒนธรรม': 'earned_credits_category_5',
    '6 ด้านกิจกรรมอื่นๆ': 'earned_credits_category_6',
}

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def homeFacultyStaff(request):
    user_faculty_staff = get_object_or_404(UserFacultyStaff, user=request.user)
    activity_type = request.GET.get('activity_type', 'all')
    def update_student_credit(selected_activity, is_approval):
        students_in_activity = ActivityParticipant.objects.filter(
            activity=selected_activity,
            is_approved=True
        ).select_related('user_student')
        activity_year = selected_activity.academic_year
        field_name = CREDIT_FIELD_MAPPING.get(selected_activity.activity_type)
        credit_amount = selected_activity.credit
        if not field_name:
            return False
        operator = 1 if is_approval else -1 
        for item in students_in_activity:
            student = item.user_student
            credit_year, created = StudentYearlyActivityCredit.objects.get_or_create(
                student=student,
                academic_year=activity_year,
                defaults={
                    'year_level': getattr(student, 'current_year', 1) 
                }
            )
            current_credit = getattr(credit_year, field_name)
            new_credit = current_credit + (operator * credit_amount)
            if not is_approval and new_credit < 0:
                new_credit = 0 
            setattr(credit_year, field_name, new_credit)
            credit_year.save()
        return True
    if activity_type == 'all':
        activities = Activity.objects.filter(
            Q(user_faculty_staff=user_faculty_staff) | 
            Q(user_responsible__faculty=user_faculty_staff.faculty)
        )
    else:
        activities = Activity.objects.filter(
            Q(user_faculty_staff=user_faculty_staff) | 
            Q(user_responsible__faculty=user_faculty_staff.faculty),
            activity_type=activity_type
        )
            
    if request.method == 'POST':
        if 'approve_activity' in request.POST:
            activity_id = request.POST.get('approve_activity')
            selected_activity = get_object_or_404(Activity, id=activity_id)

            if not selected_activity.is_approved:
                update_student_credit(selected_activity, is_approval=True)
                selected_activity.is_approved = True
                selected_activity.save()

        elif 'cancel_approval' in request.POST:
            activity_id = request.POST.get('cancel_approval')
            selected_activity = get_object_or_404(Activity, id=activity_id)

            if selected_activity.is_approved:
                update_student_credit(selected_activity, is_approval=False)
                selected_activity.is_approved = False
                selected_activity.save()

    return render(request, 'FacultyStaff/homeFacultyStaff.html', {
        'db': activities,
        'user_facultystaff': user_faculty_staff,
        'act_choices': act_choices[:], 
        'registered_students' : activities,
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def create_activity_FacultyStaff(request):
    user_facultystaff = UserFacultyStaff.objects.get(user=request.user)
    form = ActivityForm()
    if request.method == 'POST':
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user_faculty_staff = user_facultystaff
            activity.save()
            return redirect('create_activity_timeevent_FacultyStaff', activity_id=activity.id)

    return render(request, 'FacultyStaff/create_activity_FacultyStaff.html', {
        'form' : form,
        'user_facultystaff' : user_facultystaff
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def create_activity_timeevent_FacultyStaff(request, activity_id):
    user_facultystaff = UserFacultyStaff.objects.get(user=request.user)
    activity = get_object_or_404(Activity, id=activity_id)
    num_of_days = activity.number_of_days

    if request.method == 'POST':
        form = ActivityTimeEventForm(request.POST, request.FILES, num_of_days=num_of_days)
        if form.is_valid():
            for i in range(num_of_days):
                time_event = ActivityTimeEvent(
                    activity=activity,
                    start_date_activity=form.cleaned_data[f'start_date_activity_{i}'],
                    due_date_activity=form.cleaned_data[f'due_date_activity_{i}'],
                    place=form.cleaned_data[f'place{i}']
                )
                time_event.save()
            return redirect('home_activity_FacultyStaff')
    else:
        form = ActivityTimeEventForm(num_of_days=num_of_days)

    return render(request, 'FacultyStaff/create_activity_timeevent_FacultyStaff.html', {
        'form': form,
        'activity': activity,
        'user_facultystaff' : user_facultystaff
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def update_activity_FacultyStaff(request, activity_id):
    user_facultystaff = UserFacultyStaff.objects.get(user=request.user)
    activity_facultystaff = Activity.objects.get(pk=activity_id)
    activity_form = ActivityForm(instance=activity_facultystaff)
    if request.method == 'POST':
        activity_form = ActivityForm(request.POST, request.FILES, instance=activity_facultystaff)
        if activity_form.is_valid():
            activity = activity_form.save(commit=False)
            if activity.due_date_registration >= timezone.now():
                activity.is_registration_open = True
            else:
                activity.is_registration_open = False
            activity.save()  

            return redirect('home_activity_FacultyStaff')

    return render(request, 'FacultyStaff/update_activity_FacultyStaff.html', {
        'form': activity_form,
        'i': activity_facultystaff,
        'user_facultystaff' : user_facultystaff
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def delete_activity_FacultyStaff(request, id):
    activity = get_object_or_404(Activity, pk=id)
    user_obj = UserFacultyStaff.objects.get(user=request.user)
    if activity.user_faculty_staff != user_obj:
        return redirect('home_activity_FacultyStaff')
    else:
        activity.delete()

    return redirect('home_activity_FacultyStaff')

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def check_student_list_FacultyStaff(request, activity_id):
    user_facultystaff = UserFacultyStaff.objects.get(user=request.user)
    activity_faculty_staff = get_object_or_404(Activity, id=activity_id)
    students_in_activity = ActivityParticipant.objects.filter(activity=activity_faculty_staff).select_related('user_student')

    if request.method == 'POST':
        selected_students = request.POST.getlist('student')
        
        for student_in_activity in students_in_activity:
            if str(student_in_activity.user_student.id) in selected_students:
                student_in_activity.is_approved = True
            else:
                student_in_activity.is_approved = False
              
            student_in_activity.save(update_fields=['is_approved'])

        return redirect('home_activity_FacultyStaff')
    
    return render(request, 'FacultyStaff/check_student_list_FacultyStaff.html', {
        'activity_faculty_staff': activity_faculty_staff,
        'students_in_activity': students_in_activity,
        'user_facultystaff' : user_facultystaff
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def upload_pdf_FacultyStaff(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    if ActivityPdf.objects.filter(activity=activity).exists():
        return redirect('home_activity_FacultyStaff')

    if request.method == 'POST':
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            ActivityPdf.objects.create(activity=activity, pdf_file=pdf_file)
            return redirect('home_activity_FacultyStaff')
        else:
            return redirect('home_activity_FacultyStaff')

    return render(request, 'FacultyStaff/home_activity.html', {'activity': activity})

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def delete_pdf_FacultyStaff(request, pdf_id):
    pdf = get_object_or_404(ActivityPdf, id=pdf_id)
    pdf.pdf_file.delete()  
    pdf.delete()  
  
    return redirect('home_activity_FacultyStaff')

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def home_activity_FacultyStaff(request):
    user_facultystaff = get_object_or_404(UserFacultyStaff, user=request.user)
    activity_type = request.GET.get('activity_type', 'all')
    if activity_type == 'all':
        activities = Activity.objects.filter(user_faculty_staff=user_facultystaff)

    return render(request, 'FacultyStaff/home_activity_FacultyStaff.html', {
        'user_facultystaff': user_facultystaff,
        'activity_person_responsible': activities,
        'act_choices': act_choices[:],
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def download_activity_csv_FacultyStaff(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    students_in_activity = ActivityParticipant.objects.filter(activity=activity).select_related('user_student')
    filename = f"รายชื่อผู้เข้าร่วม_{activity.activity_name}.csv"
    encoded_filename = iri_to_uri(filename)  
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    writer = csv.writer(response)
    for student in students_in_activity:
        writer.writerow([student.user_student.user.username, activity.credit])

    return response

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def generate_pdf_sign_up_form_FacultyStaff(request, id):
    db_user = ActivityParticipant.objects.filter(activity_id=id)
    time_events = ActivityTimeEvent.objects.filter(activity_id=id)  
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    if db_user.exists():
        pdf.title = ('แบบบันทึกการเข้าร่วมกิจกรรม ' + db_user.first().activity.activity_name)
    else:
        pdf.title = 'แบบบันทึกการเข้าร่วมกิจกรรม'

    story = []
    font_path = os.path.join(settings.BASE_DIR, 'ActivityParticipationManagementSystem', 'path_to_fonts', 'THSarabunNew.ttf')

    if not os.path.exists(font_path):
        return HttpResponse(f"Font file not found at {font_path}", status=404)

    pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ThaiStyle', fontName='THSarabunNew', fontSize=16, leading=20))
    styles.add(ParagraphStyle(name='TableHeaderStyle', fontName='THSarabunNew', fontSize=14, alignment=1))
    styles.add(ParagraphStyle(name='TableCellStyle', fontName='THSarabunNew', fontSize=14, alignment=0))
    styles.add(ParagraphStyle(name='CenteredStyle', fontName='THSarabunNew', fontSize=16, alignment=1))

    if db_user.exists():
        activity_name = db_user.first().activity.activity_name
        for time_event in time_events:
            start_date_activity_thai = timezone.localtime(time_event.start_date_activity)
            due_date_activity_thai = timezone.localtime(time_event.due_date_activity)
            story.append(Paragraph(f"รายชื่อผู้เข้าร่วมกิจกรรม {activity_name}", styles['CenteredStyle']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"สถานที่: {time_event.place}", styles['CenteredStyle']))
            story.append(Paragraph(f"วันที่: {start_date_activity_thai.strftime('%d/%m/%Y')}", styles['CenteredStyle']))
            story.append(Paragraph(f"เวลา: {start_date_activity_thai.strftime('%H:%M')} - {due_date_activity_thai.strftime('%H:%M')}", styles['CenteredStyle']))
            story.append(Spacer(1, 12))
            data = [['ลำดับ', 'ชื่อ-สกุล', 'รหัสนักศึกษา', 'คณะ', 'ลงชื่อ']]
            for index, user in enumerate(db_user, start=1):
                full_name = f"{user.user_student.title} {user.user_student.user.first_name} {user.user_student.user.last_name}"
                student_id = user.user_student.user.username
                faculty = user.user_student.faculty
                data.append([str(index), full_name, student_id, faculty, ""])

            table = Table(data, colWidths=[50, 150, 100, 100, 100])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'THSarabunNew'),
                ('FONTSIZE', (0, 0), (-1, 0), 16),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12)]))
            story.append(table)
            story.append(Spacer(1, 24)) 
            story.append(PageBreak())
    else:
        story.append(Paragraph("ไม่พบข้อมูลผู้เข้าร่วมกิจกรรม", styles['CenteredStyle']))

    pdf.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

    return render(request, 'FacultyStaff/generate_pdf_sign_up_form_FacultyStaff.html', {'pdf_base64': pdf_base64, 'activity_id': id})

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def generate_pdf_registration_form_FacultyStaff(request, id):
    activityparticipant = ActivityParticipant.objects.filter(activity_id=id)
    activitytimeEvent = ActivityTimeEvent.objects.filter(activity_id=id)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    font_path = os.path.join(settings.BASE_DIR, 'ActivityParticipationManagementSystem', 'path_to_fonts', 'THSarabunNew.ttf')
    pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))
    pdf.setFont("THSarabunNew", 14)
    # pdf.setTitle('แบบบันทึกการเข้าร่วมกิจกรรม ' + activityparticipant.first().activity.activity_name)
    pdf.drawCentredString(10.5 * cm, 28.5 * cm, "แบบบันทึกการเข้าร่วมกิจกรรมของนักศึกษามหาวิทยาลัยอุบลราชธานี")
    pdf.drawString(2 * cm, 27.5 * cm, "ชื่อกิจกรรม (ภาษาไทย) _________________________________________________________________________________")
    # pdf.drawString(6.5 * cm, 27.5 * cm, activityparticipant.first().activity.activity_name)
    pdf.drawString(2 * cm, 26.7 * cm, "ชื่อกิจกรรม (ภาษาอังกฤษ) _______________________________________________________________________________")  # ลดช่องไฟลงเล็กน้อย
    pdf.drawString(6.5 * cm, 26.7 * cm, "")
    pdf.drawString(2 * cm, 25.9 * cm, "หน่วยงานที่จัดกิจกรรม")  
    pdf.rect(7 * cm, 25.7 * cm, 0.4 * cm, 0.4 * cm)   
    pdf.drawString(7.5 * cm, 25.8 * cm, "หน่วยงานภายใน")
    pdf.line(7.1 * cm, 25.8 * cm, 7.3 * cm, 26 * cm)
    pdf.rect(12 * cm, 25.7 * cm, 0.4 * cm, 0.4 * cm)  
    pdf.drawString(12.5 * cm, 25.8 * cm, "หน่วยงานภายนอก")
    pdf.drawString(7 * cm, 25.1 * cm, "โปรดระบุชื่อหน่วยงาน _____________________________________________________")
    pdf.drawString(11 * cm, 25.3 * cm, "")
    pdf.drawString(2 * cm, 24.3 * cm, "ด้านกิจกรรม")  
    pdf.rect(4 * cm, 24.1 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 24.3 * cm, "วิชาการที่ส่งเสริมคุณลักษณะบัณฑิต")
    pdf.drawString(5 * cm, 23.8 * cm, "ที่พึงประสงค์")
    pdf.rect(4 * cm, 23.3 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 23.3 * cm, "กีฬา หรือการส่งเสริมสุขภาพ")
    pdf.rect(4 * cm, 22.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 22.5 * cm, "บำเพ็ญประโยชน์ หรือรักษาสิ่งแวดล้อม")
    pdf.rect(4 * cm, 21.7 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 21.7 * cm, "เสริมสร้างคุณธรรม และจริยธรรม")
    pdf.rect(4 * cm, 20.9* cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(5 * cm, 20.9 * cm, "ส่งเสริมศิลปะ และวัฒนธรรม")
    pdf.rect(14 * cm, 24.1 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(12 * cm, 24.3 * cm, "ด้านกิจกรรม")
    pdf.drawString(12 * cm, 23.8 * cm, "ตาม TQF")
    pdf.drawString(15 * cm, 24.3 * cm, "ด้านคุณธรรมจริยธรรม")
    pdf.rect(14 * cm, 23.3 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 23.5 * cm, "ด้านความรู้")
    pdf.rect(14 * cm, 22.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 22.7 * cm, "ด้านทักษะทางปัญญา")
    pdf.rect(14 * cm, 21.7 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 21.9 * cm, "ด้านความสัมพันธ์ระหว่างบุคคล")
    pdf.drawString(15 * cm, 21.4 * cm, "ความรับผิดชอบ")
    pdf.rect(14 * cm, 20.5 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(15 * cm, 20.5 * cm, "ด้านการวิเคราะห์เชิงตัวเลข การสื่อสาร")
    pdf.drawString(15 * cm, 20.0 * cm, "และการใช้เทคโนโลยี สารสนเทศ")
    pdf.drawString(2 * cm, 19.5 * cm, "จำนวนชั่วโมงที่เข้าร่วมกิจกรรม ________________") 
    # hours = activityparticipant.first().activity.credit * 3
    # pdf.drawString(7.5 * cm, 19.5 * cm, str(hours))
    pdf.drawString(9 * cm, 19.5 * cm, "ชั่วโมง")
    pdf.drawString(12 * cm, 19.5 * cm, "จำนวนผู้เข้าร่วม (เป้าหมาย) ______________")
    # pdf.drawString(17 * cm, 19.5 * cm, str(activityparticipant.first().activity.max_participants))
    pdf.drawString(18.2 * cm, 19.5 * cm, "คน")
    pdf.drawString(2 * cm, 18.5 * cm, "วันที่เริ่ม ________________")
    pdf.drawString(6 * cm, 18.5 * cm, "เวลา ________________________")
    pdf.drawString(11 * cm, 18.5 * cm, "วันที่สิ้นสุด __________________")
    pdf.drawString(15.7 * cm, 18.5 * cm, "เวลา ____________________")
    # responsible_person_t = activityparticipant.first().activity.user_responsible.title
    # responsible_person_f = activityparticipant.first().activity.user_responsible.user.first_name
    # responsible_person_l = activityparticipant.first().activity.user_responsible.user.last_name
    pdf.drawString(2 * cm, 17.5 * cm, "ผู้รับผิดชอบโครงการ ___________________________________")
    # pdf.drawString(5 * cm, 17.5 * cm, responsible_person_t)
    # pdf.drawString(6 * cm, 17.5 * cm, responsible_person_f)
    # pdf.drawString(9 * cm, 17.5 * cm, responsible_person_l)
    pdf.drawString(11 * cm, 17.5 * cm, "ที่ปรึกษาโครงการ ______________________________________")
    pdf.drawString(5 * cm, 16.7 * cm, str(activitytimeEvent.first().place))
    pdf.drawString(2 * cm, 16.7 * cm, "สถานที่จัดกิจกรรม _________________________________________________________________________________________")
    pdf.drawString(5.5 * cm, 16.5 * cm, "")
    pdf.drawString(2 * cm, 16 * cm, "งบประมาณ")
    pdf.rect(4 * cm, 15.8 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 15.8 * cm, "เงินงบประมาณแผ่นดิน _____________________________")
    pdf.drawString(13 * cm, 15.8 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 15.8 * cm, "บาท")
    pdf.rect(4 * cm, 15 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 15 * cm, "เงินรายได้มหาวิทยาลัย _____________________________")
    pdf.drawString(13 * cm, 15 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 15 * cm, "บาท")
    pdf.rect(4 * cm, 14.2 * cm, 0.4 * cm, 0.4 * cm)
    pdf.drawString(4.7 * cm, 14.2 * cm, "เงินรายได้อื่นๆ (โปรดระบุ) __________________________")
    pdf.drawString(13 * cm, 14.2 * cm, "จำนวนเงิน _______________________")
    pdf.drawString(18.5 * cm, 14.2 * cm, "บาท")
    pdf.drawString(2 * cm, 13.5 * cm, "คำอธิบายเกี่ยวกับ")
    pdf.drawString(2 * cm, 13.1 * cm, "กิจกรรม")
    pdf.drawString(6 * cm, 13.1 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 12.4 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 11.7 * cm, "________________________________________________________________________________")
    pdf.drawString(2 * cm, 11.5 * cm, "รายชื่อนักศึกษาที่เข้าร่วม")
    pdf.drawString(2 * cm, 11 * cm, "(กรุณาระบุ ชื่อ-สกุล คณะ")
    pdf.drawString(2 * cm, 10.5 * cm, "รหัสนักศึกษา หมายเลขติดต่อ")
    pdf.drawString(2 * cm, 10 * cm, "ให้ครบถ้วน)")
    pdf.drawString(6 * cm, 11 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 10.3 * cm, "________________________________________________________________________________")
    pdf.drawString(6 * cm, 9.6 * cm, "________________________________________________________________________________")
    pdf.drawString(5 * cm, 9 * cm, "หมายเหตุ : โปรดแนบหลักฐานการเข้าร่วมกิจกรรม เช่น สําเนาโครงการ หนังสือเชิญ กําหนดการ รูปถ่าย เป็นต้น")
    pdf.drawString(6.4 * cm, 8.5 * cm, ": กรณีมีจํานวนนักศึกษาที่เข้าร่วมจํานวนมาก ให้แนบรายชื่อนักศึกษาพร้อมแบบบันทึกและชื่อรับรองทุกแผ่น")
    pdf.drawString(4 * cm, 7.5 * cm, "ข้าพเจ้าขอรับรองว่าให้เข้าร่วมกิจกรรม ตามวัน เวลา และสถานที่ที่กล่าวจริง จึงเรียบมาเพื่อโปรดพิจารณา")
    pdf.drawString(4 * cm, 6.5 * cm, "(ลงชื่อ) _________________")
    pdf.drawString(8 * cm, 6.5 * cm, "ผู้ยื่นคำร้อง")
    pdf.drawString(12 * cm, 6.5 * cm, "(ลงชื่อ) ___________________ ผู้รับรองกิจกรรม")
    pdf.drawString(4.8 * cm, 6 * cm, "( __________________ )")
    pdf.drawString(12.8 * cm, 6 * cm, "( ___________________ )")
    pdf.drawString(4.2 * cm, 5.5 * cm, "วันที่ ___________________")
    pdf.drawString(12.2 * cm, 5.5 * cm, "วันที่ ____________________")
    pdf.rect(2 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.rect(8 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.rect(14 * cm, 1 * cm, 6 * cm, 4 * cm)
    pdf.drawString(2.5 * cm, 3.5 * cm, "(ลงชื่อ) _____________________")
    pdf.drawString(3 * cm, 3 * cm, "( _______________________ )")
    pdf.drawString(4 * cm, 2.4 * cm, "ผู้ตรวจสอบข้อมูล")
    pdf.drawString(2.5 * cm, 1.5 * cm, "วันที่ _______________________")
    pdf.drawString(8.2 * cm, 3.5 * cm, "คณะกรรมการพิจารณาแล้วเห็นสมควร")
    pdf.drawString(8.2 * cm, 3 * cm, "อนุมัติให้ค่าหน่วยกิจกรรมดังกล่าว")
    # pdf.drawString(10.5 * cm, 2.4 * cm, str(activityparticipant.first().activity.credit))
    pdf.drawString(8.3 * cm, 2.4 * cm, "จำนวน _____________ หน่วยกิจกรรม")
    pdf.drawString(16.5 * cm, 4.3 * cm, "อนุมัติ")
    pdf.drawString(14.7 * cm, 3.5 * cm, "____________________________")
    pdf.drawString(14.5 * cm, 3 * cm, "( ____________________________ )")
    pdf.drawString(14.5 * cm, 1.5 * cm, "วันที่ _______________________")
    pdf.showPage()
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

    return render(request, 'FacultyStaff/generate_pdf_registration_form_FacultyStaff.html', {
        'pdf_base64': pdf_base64, 
        'activity_id': id
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def dashboard_FacultyStaff(request):
    user_facultystaff = UserFacultyStaff.objects.get(user=request.user)

    return render(request, 'FacultyStaff/dashboard_FacultyStaff.html', {
        'user_facultystaff' : user_facultystaff
    })
#####################################################################################
def is_staff(user):
    return user.is_authenticated and hasattr(user, 'is_staff') and user.is_staff

@login_required
@user_passes_test(is_staff, login_url='login')
def homeAdmin(request):
    user_facultystaff_type = request.GET.get('is_approved', 'all')

    if user_facultystaff_type == 'all':
        user_facultystaff = UserFacultyStaff.objects.all()  
    elif user_facultystaff_type == 'approved':
        user_facultystaff = UserFacultyStaff.objects.filter(is_approved="True") 
    elif user_facultystaff_type == 'waitingapproval':
        user_facultystaff = UserFacultyStaff.objects.filter(is_approved="False")  
    else:
        user_facultystaff = UserFacultyStaff.objects.all()   

    if request.method == 'POST':
        if 'approve_user' in request.POST:
            user_id = request.POST.get('approve_user')  
            selected_facultystaff = get_object_or_404(UserFacultyStaff, id=user_id)  
            
            if not selected_facultystaff.is_approved:
                selected_facultystaff.is_approved = True  
                selected_facultystaff.save()  

                selected_facultystaff.user.is_faculty_staff = True 
                selected_facultystaff.user.save()  

        elif 'cancel_approval' in request.POST:
            user_id = request.POST.get('cancel_approval')  
            selected_facultystaff = get_object_or_404(UserFacultyStaff, id=user_id) 
            
            if selected_facultystaff.is_approved:
                selected_facultystaff.is_approved = False 
                selected_facultystaff.save()  

                selected_facultystaff.user.is_faculty_staff = False  
                selected_facultystaff.user.save()  

    return render(request, 'Admin/homeAdmin.html', {
        'user_facultystaff': user_facultystaff , 
        'faculty_choices': faculty_choices[:]  
    })

@login_required
@user_passes_test(is_staff, login_url='login')
def dashboard_Admin(request):

    return render(request, 'Admin/dashboard_Admin.html'
    )
#####################################################################################
@login_required
def dashboard_api(request):
    activity_type = request.GET.get('activity_type', 'all')
    user_faculty_staff = None
    user_responsible = None

    try:
        user_faculty_staff = UserFacultyStaff.objects.get(user=request.user)
    except UserFacultyStaff.DoesNotExist:
        pass

    try:
        user_responsible = UserResponsible.objects.get(
            user=request.user
        )
    except UserResponsible.DoesNotExist:
        pass

    if request.user.is_superuser:
        base_query = Activity.objects.all()

    elif user_faculty_staff:
        base_query = Activity.objects.filter(
            Q(user_faculty_staff=user_faculty_staff) |
            Q(user_responsible__faculty=user_faculty_staff.faculty)
        )

    elif user_responsible:
        base_query = Activity.objects.filter(
            user_responsible=user_responsible
        )

    else:
        return JsonResponse({"activities": []}, status=200)

    if activity_type != 'all':
        base_query = base_query.filter(activity_type=activity_type)

    activities_data = []

    for i in base_query:
        activity_data = {
            "activity_name": i.activity_name,
            "activity_type": i.activity_type,
            "credit": i.credit,
            "max_participants": i.max_participants, 
            "registered_count": i.registered_count, 
            "is_registration_open": i.is_registration_open,
            "is_approved": i.is_approved,
            "semester": i.semester,
            "academic_year": i.academic_year,
        }

        activity_data["staff"] = (
            {
                "username": i.user_faculty_staff.user.username,
                "first_name": i.user_faculty_staff.user.first_name,
                "last_name": i.user_faculty_staff.user.last_name,
                "faculty": i.user_faculty_staff.faculty,
            }
            if i.user_faculty_staff else None
        )

        activity_data["responsible"] = (
            {
                "username": i.user_responsible.user.username,
                "first_name": i.user_responsible.user.first_name,
                "last_name": i.user_responsible.user.last_name,
                "faculty": i.user_responsible.faculty,
            }
            if i.user_responsible else None
        )

        activities_data.append(activity_data)

    return JsonResponse({"activities": activities_data})