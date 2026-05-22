from django.shortcuts import *
from Accounts.forms import *
from django.contrib.auth.decorators import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Create your views here.
################################################################################################
def home(request):
    return render(request, 'Accounts/home.html')

def RegisterStudent(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserStudentForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_student = True
            user.save()

            student_profile = profile_form.save(commit=False)
            student_profile.user = user
            student_profile.save()

            return redirect('login')
    else:
        user_form = UserForm()
        profile_form = UserStudentForm()

    return render(request, 'Accounts/register_Student.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def RegisterResponsible(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserResponsibleForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_responsible = True
            user.save()

            responsible_profile = profile_form.save(commit=False)
            responsible_profile.user = user
            responsible_profile.save()

            return redirect('login')
    else:
        user_form = UserForm()
        profile_form = UserResponsibleForm()

    return render(request, 'Accounts/register_Responsible.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def RegisterFacultyStaff(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserFacultyStaffForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_faculty_staff = False
            user.is_approved = False
            user.save()
            faculty_staff_profile = profile_form.save(commit=False)        
            faculty_staff_profile.user = user
            faculty_staff_profile.save()

            return redirect('login')
    else:
        user_form = UserForm()
        profile_form = UserFacultyStaffForm()

    return render(request, 'Accounts/register_Facultystaff.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            if request.user.is_staff:
                return redirect('homeAdmin')
            elif request.user.is_faculty_staff:    
                return redirect('homeFacultyStaff')
            elif request.user.is_responsible:
                return redirect('homeResponsible')
            elif request.user.is_student:
                return redirect('homeStudent')
            else:
                return redirect('login')
            
    return render(request, 'Accounts/login.html')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

################################################################################################
def is_student(user):
    return user.is_authenticated and hasattr(user, 'is_student') and user.is_student

@login_required
@user_passes_test(is_student, login_url='login')
def profile_Student(request):
    user_student = get_object_or_404(UserStudent, user=request.user)
    user = request.user
    activity_records = StudentYearlyActivityCredit.objects.filter(student=user_student).order_by('academic_year')
    academic_years = activity_records.values_list('academic_year', flat=True).distinct()

    return render(request, 'ProfileStudent/profile_Student.html', {
        'user_student': user_student,
        'user': user,
        'activity_records': activity_records,
        'academic_years': academic_years,
    })

@login_required
@user_passes_test(is_student, login_url='login')
def updateprofile_Student(request, id):
    user_student = get_object_or_404(UserStudent, pk=id)
    user_form = UserUpdateForm(instance=user_student.user)
    profile_form = UserStudentUpdateForm(instance=user_student)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user_student.user)
        profile_form = UserStudentUpdateForm(request.POST, instance=user_student)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_Student')
    
    return render(request, 'ProfileStudent/updateprofile_Student.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'user_student' : user_student
    })

from django.forms import modelformset_factory
StudentYearlyActivityCreditFormSet = modelformset_factory(StudentYearlyActivityCredit, form=StudentActivityYearForm, extra=0)

@login_required
@user_passes_test(is_student, login_url='login')
def profile_Student_Credit(request, id):
    user_student = get_object_or_404(UserStudent, pk=id)

    current_thai_year = date.today().year + 543
    num_years = (user_student.years_of_study - user_student.current_year) + 1

    academic_years = [
        current_thai_year + i for i in range(num_years)
    ]

    queryset = StudentYearlyActivityCredit.objects.filter(
        student=user_student,
        academic_year__in=academic_years
    )

    if queryset.count() < num_years:
        for i, year in enumerate(academic_years):
            StudentYearlyActivityCredit.objects.get_or_create(
                student=user_student,
                academic_year=year,
                defaults={
                    'year_level': user_student.current_year + i
                }
            )

    queryset = StudentYearlyActivityCredit.objects.filter(
        student=user_student,
        academic_year__in=academic_years
    ).order_by('academic_year')

    if request.method == 'POST':
        formset = StudentYearlyActivityCreditFormSet(
            request.POST,
            queryset=queryset
        )
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                obj.student = user_student
                obj.save()
            return redirect('homeStudent')
    else:
        formset = StudentYearlyActivityCreditFormSet(queryset=queryset)

    return render(request, 'ProfileStudent/profile_Student_Credit.html', {
        'formset': formset,
        'user_student' : user_student
    })

################################################################################################
def is_responsible(user):
    return user.is_authenticated and hasattr(user, 'is_responsible') and user.is_responsible

@login_required
@user_passes_test(is_responsible, login_url='login')
def profile_Responsible(request):
    get_user_responsible = UserResponsible.objects.get(user=request.user)
    user_responsible = UserResponsible.objects.get(pk=get_user_responsible.id)
    user = request.user

    return render(request, 'ProfileResponsible/profile_Responsible.html', {
        'user_responsible' : user_responsible,
        'user' : user,
    })

@login_required
@user_passes_test(is_responsible, login_url='login')
def updateprofile_Responsible(request, id):
    user_responsible = get_object_or_404(UserResponsible, pk=id)
    user_form = UserUpdateForm(instance=user_responsible.user)
    profile_form = UserResponsibleUpdateForm(instance=user_responsible)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user_responsible.user)
        profile_form = UserResponsibleUpdateForm(request.POST, instance=user_responsible)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_Responsible')
    
    return render(request, 'ProfileResponsible/updateprofile_Responsible.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'user_responsible': user_responsible,
    })

################################################################################################
def is_faculty_staff(user):
    return user.is_authenticated and hasattr(user, 'is_faculty_staff') and user.is_faculty_staff

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def profile_FacultyStaff(request):
    get_user_facultystaff = UserFacultyStaff.objects.get(user=request.user)
    user_facultystaff = UserFacultyStaff.objects.get(pk=get_user_facultystaff.id)
    user = request.user

    return render(request, 'ProfileFacultyStaff/profile_FacultyStaff.html', {
        'user_facultystaff' : user_facultystaff,
        'user' : user,
    })

@login_required
@user_passes_test(is_faculty_staff, login_url='login')
def updateprofile_FacultyStaff(request, id):
    user_facultystaff = get_object_or_404(UserFacultyStaff, pk=id)
    user_form = UserUpdateForm(instance=user_facultystaff.user)
    profile_form = UserFacultyStaffUpdateForm(instance=user_facultystaff)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user_facultystaff.user)
        profile_form = UserFacultyStaffUpdateForm(request.POST, instance=user_facultystaff)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_FacultyStaff')
    
    return render(request, 'ProfileFacultyStaff/updateprofile_FacultyStaff.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'user_facultystaff': user_facultystaff,
    })