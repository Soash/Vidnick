from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

def generate_session_choices(start_year=2010):
    current_year = datetime.now().year + 1
    choices = []
    for year in range(start_year, current_year):
        session = f"{year}-{year + 1}"
        choices.append((session, session))
    return choices

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    Verification_CHOICES = [
        ('verified', 'Verified'),
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
    ]
    BACKGROUND_CHOICES = [
        ('Bangla', 'Bangla'),
        ('English', 'English'),
        ('Any', 'Any'),
    ]
    PAYMENT_CHOICES = [
        ('PayPal', 'PayPal'),
        ('Bank Account', 'Bank Account'),
        ('Bkash', 'Bkash'),
        ('Nagad', 'Nagad'),
        ('Rocket', 'Rocket'),
    ]
    CAMERA_CHOICES = [
        ('Webcam', 'Webcam'),
        ('Camera', 'Camera'),
        ('Mobile camera', 'Mobile camera'),
        ('Screen sharing', 'Screen sharing'),
    ]
    SESSION_CHOICES = generate_session_choices()

    
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    telegram_user_id = models.CharField(max_length=50, blank=True, null=True)
    vidnick_id = models.CharField(max_length=50, blank=True, null=True)
    facebook_id = models.URLField(blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, blank=True, null=True)
    verification = models.CharField(max_length=15, choices=Verification_CHOICES, blank=True, null=True, default='unverified')
    
    university = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    session = models.CharField(max_length=9,choices=SESSION_CHOICES, blank=True, null=True)
    
    college_name = models.CharField(max_length=100, blank=True, null=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)
    hsc_result = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ssc_result = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    language = models.CharField(max_length=15, choices=BACKGROUND_CHOICES, blank=True, null=True)
    

    camera_tools = models.CharField(max_length=50, choices=CAMERA_CHOICES, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    payment_id = models.CharField(max_length=20, blank=True, null=True)
    
    is_content_creator = models.BooleanField(default=False)
    agrees_terms = models.BooleanField(default=False)
    agrees_commission = models.BooleanField(default=False)

    image = models.ImageField(upload_to='teachers/', blank=True, null=True)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    cv = models.FileField(upload_to='cv_docs/', blank=True, null=True)
    
    total_class = models.PositiveIntegerField(default=0, blank=True, null=True)
    missed_class = models.PositiveIntegerField(default=0, blank=True, null=True)
    total_ratings_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    total_ratings = models.PositiveIntegerField(default=0, blank=True, null=True)

    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cashout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username
    
    def average_rating(self):
        if self.total_ratings_count == 0:
            return 0
        return round(self.total_ratings / self.total_ratings_count, 2)

class VidnickContact(models.Model):
    email = models.EmailField(max_length=254, unique=True, verbose_name="Email Address")
    telegram_id = models.CharField(max_length=100, unique=True, verbose_name="Telegram ID")

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Expertise(models.Model):
    EXPERTISE_TYPE = [
        ('academic', 'Academic'),
        ('skill', 'Skill')
    ]
    expertise_name = models.CharField(max_length=100)
    expertise_type = models.CharField(max_length=10, choices=EXPERTISE_TYPE)
    def __str__(self):
        return self.expertise_name

class ClassLevel(models.Model):
    class_level_name = models.CharField(max_length=100)
    serial = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.class_level_name
    
class TeacherExpertise(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_level_name = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    expertise_name = models.ForeignKey(Expertise, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=4, decimal_places=0)

    def __str__(self):
        return f"{self.class_level_name} - {self.expertise_name}"
 
class CashoutTransaction(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.user.username} - {self.transaction_id}"







