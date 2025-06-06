from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.admin.views.decorators import staff_member_required
from matchmaking.models import RequestHistory
from .forms import SignUpForm, TeacherExpertiseForm, TeacherProfileForm, generate_random_password
from .models import CustomUser, Student, Teacher, TeacherExpertise, VidnickContact, CashoutTransaction
from datetime import timedelta
import json
import uuid
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def index(request):

    current_time = timezone.now()
    vidnick_contact = VidnickContact.objects.first()
    # Update the status to "Declined"
    expired_requests = RequestHistory.objects.filter(
        requested_timestamp__lte=current_time - timedelta(hours=24),
        accepted_timestamp__isnull=True,
        status='pending'
    )
    for data in expired_requests:
        data.status = 'declined'
        data.save()

    accepted_requests = RequestHistory.objects.filter(
        status='accepted',
        meeting_status='---',
        preferred_time__lte=current_time - timedelta(minutes=10)
    )
    for data in accepted_requests:
        data.status = 'missed'
        teacher = data.teacher
        teacher.missed_class += 1
        data.save()
        # print(f"Meeting missed for {data.teacher.user.email}.")
        # Send email notification
        subject = 'Missed Meeting Notification'
        current_domain = request.get_host()
        link = f"{current_domain}/admin/matchmaking/requesthistory/?status__exact=missed/"
        message = f'Dear Admin,\n\n {data.teacher.user.username} has missed a scheduled meeting. Follow the link below to view missed meetings.\n\n{link}\n\nBest regards,\nVidnick Team'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [vidnick_contact.email],
            fail_silently=False,
        )
        # print(f"Email sent to {data.teacher.user.username} for missed meeting.")
     
    return render(request, 'index.html')

def register_view(request):
    if request.method == "POST":
        user_type = "teacher" if "teacher_signup" in request.POST else "student"
        form = SignUpForm(request.POST, user_type=user_type)
        form.request = request  # Pass request for email activation

        if form.is_valid():
            form.save()
            messages.success(request, "Check your email to activate your account.")
            return redirect("login_view")
        else:
            messages.warning(request, f"Please correct the errors below. {form.errors}")
    else:
        form = SignUpForm()

    return render(request, "users/register.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_student:
                login(request, user)
                return redirect('student_profile', username=user.username)
            if user is not None and user.is_teacher:
                login(request, user)
                return redirect('teacher_profile', username=user.username)
    else:
        form = AuthenticationForm()

    # Add Bootstrap classes to form fields
    form.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
    form.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

    return render(request, 'users/login.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('login_view')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect('signup_view')

def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                raise CustomUser.DoesNotExist
            
            new_password = generate_random_password()
            user.set_password(new_password)
            user.save()
            
            subject = 'Your account credentials'
            message = (
                f'Username: {user.username}\n'
                f'New Password: {new_password}\n\n'
                'Use this temporary password to log in, and change the password from your profile.'
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "Password reset email sent.")
        except CustomUser.DoesNotExist:
            messages.error(request, "No user is registered with this email.")
        return redirect('login_view')
    return render(request, 'users/reset_pw.html')


# In views.py
from .forms import CustomPasswordChangeForm
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            if request.user.is_student:
                return redirect('student_profile', username=request.user.username)
            return redirect('teacher_profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})










@login_required
def teacher_profile(request, username):
    if request.user.username != username:
        return redirect('index')
    
    user = get_object_or_404(CustomUser, username=username, is_teacher=True)
    teacher = get_object_or_404(Teacher, user=user)
    context = {
        'user': user,
        'teacher': teacher,
    }
    return render(request, 'users/tprofile.html', context)


@login_required
def student_profile(request, username):
    if request.user.username != username:
        return redirect('index')
    
    user = get_object_or_404(CustomUser, username=username, is_student=True)
    student = get_object_or_404(Student, user=user)
    context = {
        'user': user,
        'student': student,
    }
    return render(request, 'users/sprofile.html', context)



@login_required
def update_teacher_profile(request):
    user = request.user
    teacher = get_object_or_404(Teacher, user=user) 
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('teacher_profile', username=user.username)
    else:
        form = TeacherProfileForm(instance=teacher)
    
    return render(request, 'users/tprofile_update.html', {'form': form, 'teacher': teacher})



from django.http import HttpResponseRedirect

@login_required
def send_verification_email(request):
    # print("Request method:", request.method)
    if request.method == "POST":
        teacher = get_object_or_404(Teacher, user=request.user)

        required_fields = [
            teacher.phone,
            teacher.address,
            teacher.gender,
            teacher.university,
            teacher.department,
            teacher.session,
            teacher.hsc_result,
            teacher.ssc_result,
            teacher.language,
            teacher.camera_tools,
            teacher.payment_method,
            teacher.payment_id,
            teacher.image,
            teacher.verification_document,
            teacher.cv,
        ]

        if not all(required_fields):
            # print("Missing required fields:", [field for field in required_fields if not field])
            messages.warning(request, "Please complete all required profile information before requesting verification.")
            return redirect('update_teacher_profile')  # Update this if your URL name differs

        vidnick_contact = VidnickContact.objects.first()
        if not vidnick_contact:
            return redirect('teacher_profile', username=request.user.username)

        teacher.verification = 'pending'
        teacher.save()

        current_domain = request.get_host()
        verification_link = f"{current_domain}/admin/users/teacher/?verification__exact=pending/"
        subject = "Verification Request"
        message = (
            f"Hello Admin,\n\n"
            f"A verification request has been initiated for the following teacher.\n\n"
            f"User: {teacher.user.username}\n"
            f"Vidnick ID: {teacher.vidnick_id}\n\n"
            f"Please click the link below to view pending verifications.\n"
            f"{verification_link}\n\n"
            f"Thank you."
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [vidnick_contact.email],
            fail_silently=False,
        )

        messages.success(request, "Verification request sent successfully.")
        return redirect('teacher_profile', username=request.user.username)

    # Handle GET requests (prevent errors when accessing the URL directly)
    return HttpResponseRedirect('/')  # Or show a 405 page, or redirect to profile




@staff_member_required
def pending_verification(request):
    pending_teachers = Teacher.objects.filter(verification='pending')
    return render(request, 'users/pending_verification.html', {'pending_teachers': pending_teachers})

    
@staff_member_required
def missed_requests_view(request):
    missed_requests = RequestHistory.objects.filter(status='missed')
    return render(request, 'users/missed_requests.html', {'missed_requests': missed_requests})






def generate_transaction_id():
    return uuid.uuid4().hex[:10]


@login_required
def cashout_view(request):
    user = request.user
    user = get_object_or_404(CustomUser, username=user.username, is_teacher=True)
    teacher = get_object_or_404(Teacher, user=user)
    cashout_transactions = CashoutTransaction.objects.filter(teacher=teacher)
    
    if request.method == 'POST':
        if teacher.verification == 'verified' and teacher.current_balance > 0:
            amount = teacher.current_balance
            teacher.total_cashout += amount
            teacher.current_balance = 0
            teacher.save()
            
            # Create a new cashout transaction
            CashoutTransaction.objects.create(
                teacher=teacher,
                amount=amount,
                transaction_id=generate_transaction_id()  # You need to implement this function
            )
            
            messages.success(request, "Cashout successful.")
        else:
            messages.error(request, "You cannot cashout now. Please verify your profile or ensure you have a positive balance.")
        return redirect('cashout_view')
    
    context = {
        'user': user,
        'teacher': teacher,
        'cashout_transactions': cashout_transactions,
    }
    return render(request, 'users/cashout.html', context)


def logout_view(request):
    logout(request)
    return redirect('index')


def custom_404_view(request, exception):
    return render(request, 'users/404.html', status=404)


@csrf_exempt
def send_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            email = data.get("email")
            message = data.get("message")
            
            # print("Contact Form Data:=\n", data)
            # print(f"Name: {name}\nEmail: {email}\nMessage: {message}")
            
            subject=f"New Contact Form Submission from {name}"
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            
            vidnick_contact = VidnickContact.objects.first()
            if not vidnick_contact:
                return redirect('index')
                        
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [vidnick_contact.email],
                fail_silently=False,
            )

            return JsonResponse({"success": True, "message": "Email sent successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


def developer_view(request):
    return render(request, 'users/developer.html')








from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import TeacherExpertise, Teacher, Expertise, ClassLevel
from .forms import TeacherExpertiseForm
from django.views import View

class TeacherExpertiseListView(ListView):
    model = TeacherExpertise
    template_name = 'users/teacher_expertise_list.html'
    
    def get_queryset(self):
        self.teacher = get_object_or_404(Teacher, id=self.kwargs['teacher_id'])
        return TeacherExpertise.objects.filter(teacher=self.teacher)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = self.teacher
        return context


class TeacherExpertiseCreateView(CreateView):
    model = TeacherExpertise
    form_class = TeacherExpertiseForm
    template_name = 'users/teacher_expertise_form.html'

    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, id=self.kwargs['teacher_id'])
        form.instance.teacher = teacher
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('teacher_expertise_list', kwargs={'teacher_id': self.kwargs['teacher_id']})


class TeacherExpertiseUpdateView(UpdateView):
    model = TeacherExpertise
    form_class = TeacherExpertiseForm
    template_name = 'users/teacher_expertise_form.html'

    def get_success_url(self):
        return reverse_lazy('teacher_expertise_list', kwargs={'teacher_id': self.object.teacher.id})


class TeacherExpertiseDeleteView(View):
    def post(self, request, teacher_id, pk):
        expertise = get_object_or_404(TeacherExpertise, pk=pk, teacher__id=teacher_id)
        expertise.delete()
        return redirect('teacher_expertise_list', teacher_id=teacher_id)
