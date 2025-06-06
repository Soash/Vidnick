import uuid, json, math, requests, pytz, traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import RequestHistory, Reports, ExpertiseRequest, Teacher
from .utils import send_telegram_notification, generate_jitsi_meeting_url
from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from users.models import Expertise, Student, Teacher, TeacherExpertise, VidnickContact
from environ import Env
from decimal import Decimal
from firebase_admin.exceptions import FirebaseError
from datetime import datetime
import traceback
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import FindBrowseExpertForm
from .models import RequestHistory
from django.shortcuts import get_object_or_404, redirect
from .models import RequestHistory, Teacher
from django.views.generic import DetailView

env = Env()
Env.read_env()
BASE_DIR = settings.BASE_DIR

cred = credentials.Certificate("vidnick.json")
firebase_admin.initialize_app(cred)

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')


# @login_required
# def find_teacher(request):
#     if request.method == 'POST':
#         try:
#             # Step 1: Extract data from the POST request
#             subject_id = request.POST.get('subject')
#             duration = request.POST.get('duration')
#             class_field = request.POST.get('class_field')
#             medium_of_instruction = request.POST.get('medium_of_instruction')
#             gender = request.POST.get('gender')
#             preferred_time = request.POST.get('time')
#             preferred_date = request.POST.get('date')
#             note = request.POST.get('note')
#             amount = request.POST.get('amount')

#             # Ensure required fields are provided
#             if not all([subject_id, duration, preferred_time, preferred_date, amount]):
#                 return JsonResponse({'error': 'Missing required fields'}, status=400)

#             # Step 2: Validate and fetch subject or skill
#             subject, skill, teachers = None, None, None
#             if subject_id.startswith('subject_'):
#                 subject_id = int(subject_id.split('_')[1])
#                 try:
#                     subject = Expertise.objects.get(id=subject_id)
#                 except Expertise.DoesNotExist:
#                     return JsonResponse({'error': 'Subject not found'}, status=404)
#                 teachers = Teacher.objects.filter(academicexpertise__subject_name=subject).distinct()

#             elif subject_id.startswith('skill_'):
#                 skill_id = int(subject_id.split('_')[1])
#                 try:
#                     skill = Expertise.objects.get(id=skill_id)
#                 except Expertise.DoesNotExist:
#                     return JsonResponse({'error': 'Skill not found'}, status=404)
#                 teachers = Teacher.objects.filter(skillexpertise__skill_name=skill).distinct()

#             if not teachers.exists():
#                 messages.error(request, 'No teachers available.')
#                 return redirect(request.path)

#             # Step 3: Validate and parse numeric fields
#             try:
#                 duration = int(duration)
#                 amount = int(amount)
#                 if amount < 0:
#                     return JsonResponse({'error': 'Amount must be a positive integer'}, status=400)
#             except ValueError:
#                 return JsonResponse({'error': 'Invalid amount format'}, status=400)

#             # Step 4: Validate duration & minimum amount
#             MIN_AMOUNT_MAPPING = {
#                 15: 50,
#                 30: 100,
#                 45: 150,
#                 60: 200,
#                 90: 300,
#                 120: 400,
#             }

#             if duration not in MIN_AMOUNT_MAPPING:
#                 return JsonResponse({'error': 'Invalid duration selected'}, status=400)

#             min_required_amount = MIN_AMOUNT_MAPPING[duration]
#             if amount < min_required_amount:
#                 return JsonResponse({'error': f'Minimum amount for {duration} minutes is {min_required_amount} BDT'}, status=400)

#             # Step 5: Validate and parse preferred date & time
#             preferred_datetime_str = f"{preferred_date} {preferred_time}"
#             try:
#                 preferred_datetime = datetime.strptime(preferred_datetime_str, '%Y-%m-%d %I:%M %p')
#             except ValueError as e:
#                 return JsonResponse({'error': f'Invalid date or time format: {e}'}, status=400)

#             # Step 6: Fetch student profile
#             try:
#                 student = Student.objects.get(user=request.user)
#             except Student.DoesNotExist:
#                 return JsonResponse({'error': 'Student profile not found'}, status=404)


#             request_history = RequestHistory.objects.create(
#                 student=student,
#                 subject=subject,
#                 class_level=class_field,
#                 skill=skill,
#                 duration=duration,
#                 preferred_time=preferred_datetime,
#                 amount=amount,
#                 description=f"""
#                 Class: {class_field}<br>
#                 Medium: {medium_of_instruction}<br>
#                 Gender: {gender}<br>
#                 Note: {note}"""
#             )
#             request_history.all_teachers.set(teachers)

#             # Step 10: Send notifications to teachers
#             for teacher in teachers:
#                 if teacher.token:
#                     try:
#                         subject_name = request_history.subject.name if request_history.subject else request_history.skill.name
#                         message = messaging.Message(
#                             notification=messaging.Notification(
#                                 title="Vidnick",
#                                 body=f"A Student has requested to learn {subject_name}."),
#                             token=teacher.token
#                         )
#                         messaging.send(message)
#                     except Exception as e:
#                         print(f"Firebase error for {teacher.user.username}: {e}")

#                 # Send Telegram notification if teacher has a Telegram ID
#                 if teacher.telegram_user_id:
#                     try:
#                         formatted_time = request_history.preferred_time.strftime("%I:%M %p")
#                         message = (
#                             f"A Student has requested to learn.\n\n"
#                             f"Subject: {subject_name}\n"
#                             f"Preferred Time: {formatted_time}\n"
#                             f"Class: {request_history.class_level}\n"
#                             f"Duration: {request_history.duration} minutes\n"
#                             f"Amount: {amount}"
#                         )
#                         button_text = "Accept Now"
#                         button_url = "https://vidnick.com/request_history/"

#                         send_telegram_notification(
#                             teacher.telegram_user_id, 
#                             message,
#                             button_text, 
#                             button_url
#                         )
#                     except Exception as e:
#                         print(f"Error sending Telegram notification: {e}")

#             # Step 11: Redirect to student profile on success
#             return redirect('student_profile', username=request.user.username)

#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             print(traceback.format_exc())
#             return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

#     # Render form if not POST
#     form = RequestForm()
#     return render(request, 'matchmaking/find_teacher.html', {'form': form})


def filter_teachers(request_history):
    expertise = request_history.expertise_name
    class_level = request_history.class_level_name
    language = request_history.language
    gender = request_history.gender

    # Fetch teachers based on filtering criteria
    teachers = Teacher.objects.all()

    if expertise:
        teachers = teachers.filter(teacherexpertise__expertise_name=expertise)
    if class_level:
        teachers = teachers.filter(teacherexpertise__class_level_name=class_level)
    if language and language != 'Any':
        teachers = teachers.filter(language=language)
    if gender and gender != 'Any':
        teachers = teachers.filter(gender=gender)

    return teachers


class SearchTeacher(CreateView):
    model = RequestHistory
    form_class = FindBrowseExpertForm
    template_name = 'matchmaking/search_teacher.html'
    
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Add any custom logic you want to handle when the form is valid.
        if 'find-teacher' in self.request.path:
            form.instance.session_type = 'find'
        elif 'browse-teacher' in self.request.path:
            form.instance.session_type = 'browse'
        
        form.instance.student = self.request.user.student  # Assuming the user has a related student object
        
        # Save the form to create the RequestHistory instance
        response = super().form_valid(form)
        
        # Get the request history object
        request_history = form.instance
        
        # Only assign teachers if the session type is 'find'
        if request_history.session_type == 'find':
            # Now, use the filter_teachers function to get the filtered teachers
            teachers = filter_teachers(request_history)

            # Assign the filtered teachers to the `all_teachers` field
            request_history.all_teachers.set(teachers)  # Using the `set` method to add teachers

            # Save the updated request_history object
            request_history.save()

            # Add a success message
            messages.success(self.request, "Request successfully saved!")
            
            
            for teacher in teachers:
                if teacher.token:
                    try:
                        expertise_name = request_history.expertise_name
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title="Vidnick",
                                body=f"A Student has requested to learn {expertise_name}."),
                            token=teacher.token
                        )
                        messaging.send(message)
                    except Exception as e:
                        print(f"Firebase error for {teacher}: {e}")

        else:
            messages.success(self.request, "Request successfully saved!")

        # Redirect to the request history detail page
        return redirect('request_history_detail', pk=request_history.id)
    
    def form_invalid(self, form):
        # Handle any special cases for invalid form
        messages.warning(self.request, "There was an error with your submission.")
        # Print form errors to the terminal
        print(form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check the request path to determine if it's for finding or browsing
        if 'find-teacher' in self.request.path:
            context['title'] = 'Find Expert'
            context['show_amount'] = True 
        elif 'browse-teacher' in self.request.path:
            context['title'] = 'Browse Expert'
            context['show_amount'] = False 
        
        return context


class RequestHistoryDetailView(DetailView):
    model = RequestHistory
    template_name = 'matchmaking/session_detail.html'
    context_object_name = 'request_history'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the current request history object
        request_history = self.get_object()

        # Use the filter_teachers function to get the filtered teachers
        teachers = filter_teachers(request_history)

        print(teachers)
        
        # Prepare the teacher list with necessary details
        teacher_list = []
        assigned_teacher_list = []
        
        for teacher in teachers:
            teacher_expertise = TeacherExpertise.objects.filter(
                teacher=teacher, 
                expertise_name=request_history.expertise_name, 
                class_level_name=request_history.class_level_name
            ).first()
            rate = teacher_expertise.rate if teacher_expertise else "N/A"

            if teacher in request_history.all_teachers.all():
                assigned_teacher_list.append({'id': teacher.id, 'vidnick_id': teacher.vidnick_id, 'university': teacher.university, 'rate': str(rate),})
            else:
                teacher_list.append({'id': teacher.id, 'vidnick_id': teacher.vidnick_id, 'university': teacher.university, 'rate': str(rate),})

        # Add the available teachers and assigned teachers to the context
        context['teachers'] = teacher_list
        context['assigned_teachers'] = assigned_teacher_list
        
        return context



@login_required
def assign_teacher(request, request_history_id, teacher_id):
    request_history = get_object_or_404(RequestHistory, id=request_history_id)
    teacher = get_object_or_404(Teacher, id=teacher_id)

    # Assign the teacher to the request history (adjust according to your model relationship)
    request_history.all_teachers.add(teacher)  # Example of many-to-many relationship

    messages.success(request, "Request successfully send!")
    # return redirect('request_history_detail', pk=request_history.id)
    return redirect(f"{request_history.get_absolute_url()}#assigned-teachers-table")

@login_required
def delete_teacher(request, request_history_id, teacher_id):
    request_history = get_object_or_404(RequestHistory, id=request_history_id)
    teacher = get_object_or_404(Teacher, id=teacher_id)

    # Assign the teacher to the request history (adjust according to your model relationship)
    request_history.all_teachers.remove(teacher)  # Correct method for many-to-many relationship

    messages.success(request, "Request successfully removed!")
    # return redirect('request_history_detail', pk=request_history.id)
    return redirect(f"{request_history.get_absolute_url()}#assigned-teachers-table")


@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    pending_requests = RequestHistory.objects.filter(
        status='pending', all_teachers=teacher
    ).order_by('-requested_timestamp')


    # Get accepted requests assigned to this teacher
    accepted_requests = RequestHistory.objects.filter(
        teacher=teacher, status='accepted'
    ).order_by('-requested_timestamp')

    current_time = timezone.now()

    # Process accepted requests
    for req in accepted_requests:
        if req.preferred_time:
            time_difference = (req.preferred_time - current_time).total_seconds() / 60
            req.start_within_time_frame = -3 <= time_difference <= 10
        else:
            req.start_within_time_frame = False

        if req.start_time and not req.end_time:
            duration = (timezone.now() - req.start_time).total_seconds() / 60
            req.claim_btn = duration > req.duration
        else:
            req.claim_btn = False

    return render(
        request, 'matchmaking/teacher_dashboard.html',
        {
            'pending_requests': pending_requests,
            'accepted_requests': accepted_requests,
            'teacher': teacher
        }
    )

@login_required
def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    history = RequestHistory.objects.filter(student=student).order_by('-requested_timestamp')
    context = {
        'rating_range': range(10, 0, -1),
        'history': history,
    }
    return render(request, 'matchmaking/student_dashboard.html', context)

@login_required
def accept_request(request, request_history_id):
    try:
        request_history = RequestHistory.objects.get(id=request_history_id)
        if request_history.status == 'pending':
            request_history.status = 'accepted'
            request_history.teacher = Teacher.objects.get(user=request.user)
            request_history.accepted_timestamp = timezone.now()

            if request_history.session_type == 'browse':
                teacher = request_history.teacher

                expertise = TeacherExpertise.objects.get(teacher=teacher, expertise_name=request_history.expertise_name, class_level_name=request_history.class_level_name)
    
                if expertise:
                    hourly_rate = Decimal(expertise.rate)
                    rate = (Decimal(request_history.duration) / Decimal(60)) * hourly_rate
                    request_history.amount = round(rate, 2)
                else:
                    request_history.amount = 0
                     
            request_history.save()
        return redirect('teacher_dashboard')
    except Exception as e:
        print(f"Error accepting request: {e}")
        return JsonResponse({'error': str(e)}, status=500)





@login_required
def start_jitsi_meeting(request, request_id):
    # Fetch the request history based on the ID passed in the URL
    try:
        request_history = RequestHistory.objects.get(id=request_id)
    except RequestHistory.DoesNotExist:
        return HttpResponseNotFound("Request not found")

    # Check if the Zoom meeting already exists, if not create it
    if not request_history.meeting_id:
        # Create the Jitsi meeting
        meeting_info = generate_jitsi_meeting_url()

        # Save the Jitsi meeting details to RequestHistory
        request_history.meeting_id = meeting_info['id']
        request_history.join_url = meeting_info['join_url']
        request_history.start_url = meeting_info['start_url']
        request_history.meeting_status = "start"
        request_history.save()
                
    return redirect(request_history.join_url)

@login_required
def join_jitsi_meeting(request, request_id):
    try:
        request_history = RequestHistory.objects.get(id=request_id)
    except RequestHistory.DoesNotExist:
        return HttpResponseNotFound("Request not found")
    request_history.start_time = timezone.now()
    request_history.save()
    return redirect(request_history.join_url)

@login_required
def meeting_end(request, meeting_id):
    # Get the RequestHistory object
    req_history = get_object_or_404(RequestHistory, meeting_id=meeting_id)
    if not req_history.start_time:
        req_history.start_time = timezone.now()
        req_history.save()
    # Check if a meeting ID exists
    if req_history.meeting_id:

        req_history.end_time = timezone.now()
        req_history.save()
        print(req_history.start_time)
        print(req_history.end_time)
        duration = req_history.end_time - req_history.start_time
        duration_in_minutes = duration.total_seconds() / 60
        
        if duration_in_minutes > req_history.duration:
            req_history.total_duration = req_history.duration
        else:
            req_history.total_duration = math.ceil(duration_in_minutes)
            
        if req_history.total_duration < 5:
            req_history.refund_eligibility = True
            req_history.refund_status = 'unpaid'
            req_history.refund_amount = req_history.amount
        elif req_history.total_duration < req_history.duration / 2:
            req_history.refund_eligibility = True
            req_history.refund_status = 'upaid'
            req_history.refund_amount = req_history.amount / 2
        else:
            req_history.refund_eligibility = False
            req_history.refund_status = 'paid'
            req_history.refund_amount = 0
            
        req_history.meeting_status = 'end'
        req_history.save()
        
        # Update teacher's balance
        teacher = req_history.teacher
        net_amount = req_history.amount - req_history.refund_amount
        teacher.current_balance += net_amount * Decimal(0.8)
        teacher.total_income += net_amount * Decimal(0.8)
        
        teacher.total_class += 1
        teacher.save()
        
        #send push notification
        if req_history.teacher.token:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                    title="Vidnick",
                    body="Your meeting has ended by student."
                    ),
                    token=req_history.student.token
                )
                response = messaging.send(message)
                print(f"Push notification sent: {response}")
            except FirebaseError as e:
                print(f"Firebase error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        
        # Send Telegram notification
        if req_history.teacher.telegram_user_id:
            try:
                message = f"Meeting with ID {req_history.meeting_id} has ended.\nDuration: {req_history.total_duration} minutes."
                button_text = "Vidnick"
                button_url = "vidnick.com"
                send_telegram_notification(
                    req_history.teacher.telegram_user_id, 
                    message,
                    button_text, 
                    button_url
                )
            except Exception as e:
                print(f"Error sending Telegram notification: {e}")
            
        # Send email notification
        try:
            subject = "Meeting Ended Notification"
            message = f"Dear {req_history.teacher.user.first_name},\n\nYour meeting with ID {req_history.meeting_id} has ended. Duration: {req_history.total_duration} minutes."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [req_history.teacher.user.email]
            send_mail(subject, message, from_email, recipient_list)
            print("Email notification sent.")
        except Exception as e:
            print(f"Error sending email notification: {e}")

    else:
        messages.warning(request, "No meeting ID found for this request.")

    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    return redirect('request_history')

















@login_required
def submit_rating(request, request_id):
    if request.method == "POST":
        req_instance = get_object_or_404(RequestHistory, id=request_id)
        teacher = req_instance.teacher

        try:
            rating = int(request.POST.get("rating", 0))
            if 1 <= rating <= 10:
                # Check if the rating is being updated
                if req_instance.ratings:
                    # Adjust the teacher's total ratings and class count
                    teacher.total_ratings -= req_instance.ratings
                    teacher.total_ratings += rating
                else:
                    # Add new rating
                    teacher.total_ratings_count += 1
                    teacher.total_ratings += rating
                
                # Update the request instance with the new rating
                req_instance.ratings = rating
                req_instance.save()

                # Save the updated teacher record
                teacher.save()
                messages.success(request, "Rating submitted successfully!")
            else:
                messages.error(request, "Invalid rating. Please choose a value between 1 and 10.")
        except ValueError:
            messages.error(request, "Invalid input. Please enter a valid number.")
    
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def submit_report(request, request_id):
    if request.method == "POST":
        req_instance = get_object_or_404(RequestHistory, id=request_id)
        student = req_instance.student
        teacher = req_instance.teacher
        description = request.POST.get("description", "").strip()

        if not description:
            messages.error(request, "Report description cannot be empty.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Create a report entry
        Reports.objects.create(student=student, teacher=teacher, description=description, req_history=req_instance)
        
        vidnick_contact = VidnickContact.objects.first()
        if not vidnick_contact:
            return redirect('teacher_profile', username=request.user.username)
        
        current_domain = request.get_host()
        link = f"{current_domain}/admin/matchmaking/reports/"
        
        subject = "A student reported about a meeting"
        message = (
            f"Hello Admin,\n\n"
            f"Please check the report.\n"
            f"{description}\n"
            f"{link}\n\n"
            f"Thank you."
        )

        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [vidnick_contact.email],
            fail_silently=False,
        )
        print("Email notification sent.")
        messages.success(request, "Your report has been submitted successfully.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def request_subject_skill(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            ExpertiseRequest.objects.create(
                description=description,
                created_by=request.user  # Associate the logged-in user
            )
            
            vidnick_contact = VidnickContact.objects.first()
            if not vidnick_contact:
                return redirect('teacher_profile', username=request.user.username)
            
            current_domain = request.get_host()
            link = f"{current_domain}/admin/matchmaking/requestedsubjectskill/"
            
            subject = "Request to add skill/subject"
            message = (
                f"Hello Admin,\n\n"
                f"Please add the subject/skill.\n"
                f"{description}\n"
                f"{link}\n\n"
                f"Thank you."
            )

            # Send the email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [vidnick_contact.email],
                fail_silently=False,
            )
            print("Email notification sent.")
            messages.success(request, "Your request has been submitted successfully.")
        else:
            messages.error(request, "Please provide a valid description.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    return HttpResponseNotFound("Page not found")

def meeting_log(request, request_history_id):
    # Fetch the RequestHistory object
    req_history = get_object_or_404(RequestHistory, id=request_history_id)

    # Initialize meeting data as None
    meeting_data = None

    # Check if the meeting_id exists in the RequestHistory object
    if req_history.meeting_id:
        # Try to fetch the Meeting object associated with meeting_id
        try:
            meeting = RequestHistory.objects.get(meeting_id=req_history.meeting_id)
            meeting_data = {
                'meeting_id': meeting.meeting_id,
                'start_url': meeting.start_url,
                'join_url': meeting.join_url,
                'start_time': meeting.start_time,
                'end_time': meeting.end_time,
                'duration': meeting.duration,
                'total_duration': meeting.total_duration,
                'log': meeting.log,
            }
        except RequestHistory.DoesNotExist:
            raise Http404("Meeting data not found.")
    
    context = {
        'req_history': req_history,
        'meeting_data': meeting_data,  # Add the meeting data to the context
    }
    return render(request, 'matchmaking/meeting_log.html', context)




# @csrf_exempt
@login_required
def save_token(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            token = data.get('token')
            # print(f"Saving token: {token}")
            print("Notification token saved.")
            if token:
                teacher = request.user.teacher
                if token != teacher.token:
                    # print(f"Saving token: {token} for teacher: {teacher.user.username}")
                    teacher.token = token
                    teacher.save()
                
                # Send a demo notification to verify token
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="Vidnick",
                        body=f"Test message from Vidnick"
                    ),
                    token=teacher.token
                )

                try:
                    # response = messaging.send(message)
                    # print('Message sent:', response)
                    return JsonResponse({'status': 'success', 'message': 'Notification sent successfully!'}, status=201)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Token is required'}, status=400)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)




# @csrf_exempt
@login_required
def send_demo_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')

        print("Token:", token)
        if token:
            try:
                # Create the notification message
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="Vidnick Demo",
                        body="This is a demo notification from Vidnick."),
                    token=token
                )
                # Send the message via Firebase Admin SDK
                response = messaging.send(message)
                print('Message sent:', response)
                return JsonResponse({"message": "Notification sent successfully!", "response": response})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "No token provided."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)










def initiate_payment(request, request_id):
    # SSLCommerz Credentials
    store_id = 'vidni67119c609b90f'
    store_password = 'vidni67119c609b90f@ssl'

    # Fetch the request object to get the amount
    request_instance = get_object_or_404(RequestHistory, id=request_id)
    total_amount = request_instance.amount

    # Generate a unique transaction ID
    tran_id = str(uuid.uuid4())

    # Payment Information
    payment_data = {
        'store_id': store_id,
        'store_passwd': store_password,
        'total_amount': total_amount,  # Dynamic amount
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': request.build_absolute_uri('/payment-success/'),
        'fail_url': request.build_absolute_uri('/payment-fail/'),
        'cancel_url': request.build_absolute_uri('/payment-cancel/'),
        'cus_name': 'Customer Name',
        'cus_email': 'customer@example.com',
        'cus_phone': '0123456789',
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_profile': 'non-physical-goods',
        'product_name': 'Payment for Service',
        'product_category': 'General',
    }

    # Save the transaction ID in your database
    request_instance.trans_id = tran_id
    request_instance.save()

    # Send POST request to SSLCommerz
    api_url = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
    response = requests.post(api_url, data=payment_data)
    response_data = response.json()

    # Check response and redirect user
    if response_data['status'] == 'SUCCESS':
        return redirect(response_data['GatewayPageURL'])
    else:
        return JsonResponse({'error': 'Failed to initiate payment', 'details': response_data})

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Extract SSLCommerz response
        response_data = request.POST.dict()
        tran_id = response_data.get('tran_id')

        try:
            # Retrieve the corresponding RequestHistory object
            request_instance = RequestHistory.objects.get(trans_id=tran_id)
            
            # Update payment status
            request_instance.pay_status = 'paid'
            request_instance.save()

            # Redirect to request history
            return redirect('request_history')
        except RequestHistory.DoesNotExist:
            return JsonResponse({'error': 'Request not found for the provided transaction ID.'}, status=404)
        
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def payment_fail(request):
    response_data = request.POST.dict()
    return JsonResponse({'status': 'fail', 'data': response_data})

@csrf_exempt
def payment_cancel(request):
    response_data = request.POST.dict()
    return JsonResponse({'status': 'cancel', 'data': response_data})

def initiate_refund(request, request_id):
    # SSLCommerz Credentials
    store_id = 'vidni67119c609b90f'
    store_password = 'vidni67119c609b90f@ssl'

    # Fetch the request object to get the amount
    request_instance = get_object_or_404(RequestHistory, id=request_id)

    # Payment Information
    data = {
        'store_id': store_id,
        'store_passwd': store_password,
        'refund_amount': request_instance.refund_amount,
        'bank_tran_id': request_instance.trans_id,
        'refund_remarks': 'Refund for the service',
        'format': 'json',  # Ensure response format is JSON
    }

    # Send GET request to SSLCommerz
    api_url = 'https://sandbox.sslcommerz.com/validator/api/merchantTransIDvalidationAPI.php'
    response = requests.get(api_url, params=data)  # Use params for GET request

    # Debugging: Log the raw response
    print(f"Raw Response: {response.text}")

    try:
        # Attempt to parse JSON response
        response_data = response.json()
        print(response_data)
        return JsonResponse(response_data)
    except ValueError as e:
        # Handle JSON decoding errors
        return JsonResponse({
            'error': 'Failed to parse response',
            'details': response.text  # Include raw response for debugging
        }, status=500)


