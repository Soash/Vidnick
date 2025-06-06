from django.db import models
from users.models import ClassLevel, Expertise, Teacher, Student
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

class RequestHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('missed', 'Missed'),
    ]
    MEETING_CHOICES = [
        ('start', 'Start'),
        ('end', 'End'),
        ('---', '---'),
    ]
    PAY_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('---', '---'),
    ]    
    DURATION_CHOICES = [
        (15, '15 minutes'),
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '60 minutes'),
        (90, '90 minutes'),
        (120, '120 minutes'),
    ]
    REFUND_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('---', '---'),
    ]
    BACKGROUND_CHOICES = [
        ('Bangla', 'Bangla'),
        ('English', 'English'),
        ('Any', 'Any'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Any', 'Any'),
    ]
    SESSION_TYPE_CHOICES = [
        ('find', 'find'),
        ('browse', 'browse'),
    ]


    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    all_teachers = models.ManyToManyField(Teacher, related_name='request_histories', blank=True)
    
    expertise_name = models.ForeignKey(Expertise, on_delete=models.CASCADE, null=True, blank=True)
    class_level_name = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60)
    language = models.CharField(max_length=15, choices=BACKGROUND_CHOICES, blank=True, null=True, default='Any')
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, blank=True, null=True, default='Any')
    preferred_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    note = models.TextField(max_length=50, blank=True, null=True)
    
    description = models.TextField(null=True, blank=True)
    session_type = models.CharField(max_length=9, choices=SESSION_TYPE_CHOICES, blank=True, null=True)
    
    
    requested_timestamp = models.DateTimeField(default=timezone.now)
    accepted_timestamp = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    pay_status = models.CharField(max_length=20, choices=PAY_CHOICES, default='---')
    trans_id = models.CharField(max_length=100, null=True, blank=True)
    
    meeting_id = models.CharField(max_length=100, null=True, blank=True)
    meeting_status = models.CharField(max_length=20, choices=MEETING_CHOICES, default='---')
    join_url = models.CharField(max_length=300, null=True, blank=True)
    start_url = models.CharField(max_length=900, null=True, blank=True)
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    log = models.TextField(null=True, blank=True, default='')
    total_duration = models.CharField(max_length=4, null=True, blank=True)
    
    refund_eligibility = models.BooleanField(default=False)
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='---')
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    ratings = models.PositiveIntegerField(default=0, blank=True, null=True)
    special_request = models.BooleanField(default=False)

    def __str__(self):
        return f"Request by {self.student.user.username}"
    
    def get_absolute_url(self):
        return reverse('request_history_detail', kwargs={'pk': self.pk})

    
class Reports(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reports")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="reported")
    req_history = models.ForeignKey(RequestHistory, on_delete=models.CASCADE, related_name="req_history")
    description = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.student.user.username} against {self.teacher.user.username}"
    

class ExpertiseRequest(models.Model):
    description = models.TextField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Request to add {self.description}"


