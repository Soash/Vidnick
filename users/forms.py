import random
import string
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from .models import CustomUser, Expertise, Student, Teacher
from django_select2.forms import Select2Widget
from django.conf import settings

from django import forms
from .models import TeacherExpertise
from django_select2.forms import Select2Widget

from django import forms
from .models import TeacherExpertise


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator



def generate_random_password(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_vidnick_id():
    """
    Generates a unique vidnick_id in the format VN000001.
    """
    last_teacher = Teacher.objects.order_by('-id').first()
    # print(last_teacher)
    # print(last_teacher.vidnick_id)
    if last_teacher and last_teacher.vidnick_id:
        # Extract the numeric part from the last vidnick_id
        last_id = int(last_teacher.vidnick_id[2:])  # Skip the "VN" prefix
        # print(last_id)
    else:
        last_id = 0
    
    # Increment the numeric part and format it
    new_id = last_id + 1
    return f"VN{new_id:06d}"

def generate_unique_username(first_name):
    base_username = ''.join(filter(str.isalpha, first_name)).lower()
    username = base_username
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{random.randint(1000, 9999)}"
    return username

# class TeacherSignUpForm(forms.ModelForm):
#     first_name = forms.CharField(label="Full Name", max_length=100)

#     class Meta:
#         model = CustomUser
#         fields = ('first_name', 'email')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_teacher = True
        
#         # Save first_name directly
#         first_name = self.cleaned_data.get('first_name')
#         user.first_name = first_name
        
#         user.username = generate_unique_username(first_name)
#         password = generate_random_password()
#         user.set_password(password)
        
#         if commit:
#             user.save()
#             vidnick_id = generate_vidnick_id()
#             teacher = Teacher.objects.create(user=user)
#             teacher.vidnick_id = vidnick_id
#             teacher.save()            
#             subject = 'Your account credentials'
#             message = f'Teacher Account\nUsername: {user.username}\nPassword: {password}\nVidnick ID: {vidnick_id}'
#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [self.cleaned_data.get('email')],
#                 fail_silently=False,
#             )
#         return user

# class StudentSignUpForm(forms.ModelForm):
#     first_name = forms.CharField(label="Full Name", max_length=100)
#     # grade = forms.IntegerField()

#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ('first_name', 'email')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_student = True
        
#         first_name = self.cleaned_data.get('first_name')
#         user.first_name = first_name
        
#         user.username = generate_unique_username(first_name)
#         password = generate_random_password()
#         user.set_password(password)
#         # grade = self.cleaned_data.get('grade')
#         if commit:
#             user.save()
#             # Student.objects.create(user=user, grade=grade)
#             Student.objects.create(user=user)
#             subject = 'Your account credentials'
#             message = f'Student Account\nUsername: {user.username}\nPassword: {password}'
#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [self.cleaned_data.get('email')],
#                 fail_silently=False,
#             )
#         return user







CustomUser = get_user_model()

class SignUpForm(UserCreationForm):
    def __init__(self, *args, user_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_type = user_type
         
    first_name = forms.CharField(
        label="Full Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Password',
            # 'pattern': '^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$',
            'title': "Password must be at least 8 characters long and must include both letters and numbers only"
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'confirm_password', 'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Deactivate until email confirmation
        user.first_name = self.cleaned_data.get('first_name')
        user.username = generate_unique_username(user.first_name)
        user.email = self.cleaned_data.get('email')  # Ensure formatted email is saved

        password = self.cleaned_data.get("password1")  # Retrieve inputted password

        if self.user_type == "teacher":
            user.is_teacher = True
            user_role = "Teacher"
        else:
            user.is_student = True
            user_role = "Student"

        if commit:
            user.save()  # Save user first

            if self.user_type == "teacher":
                vidnick_id = generate_vidnick_id()
                Teacher.objects.create(user=user, vidnick_id=vidnick_id)  
            else:
                Student.objects.create(user=user)  

            self.send_activation_email(user, password, user_role)  # Pass password & role

        return user

    def send_activation_email(self, user, password, user_role):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(self.request)
        activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

        subject = "Activate Your Account"
        context = {
            'user': user,
            'activation_link': activation_link,
            'username': user.username,
            'password': password,  # Include password
            'user_role': user_role  # Mention Teacher or Student
        }
        message = render_to_string('emails/account_activation.html', context)

        send_mail(
            subject,
            strip_tags(message),  # Plain text version
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=message  # Properly formatted HTML version
        )





class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ['user', 'vidnick_id', 'total_income', 'total_cashout', 'current_balance', 'verification',
                    'educational_qualification', ]

    def __init__(self, *args, **kwargs):
        super(TeacherProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.__class__.__name__ != 'CheckboxInput':
                widget.attrs['class'] = 'form-control'
            
            if widget.__class__.__name__ in ['ClearableFileInput', 'FileInput']:
                widget.attrs['class'] = 'form-control'
        
        self.fields['address'].widget.attrs.update({'rows': 3})



class TeacherExpertiseForm(forms.ModelForm):
    class Meta:
        model = TeacherExpertise
        fields = ['class_level_name', 'expertise_name', 'rate']
        widgets = {
            'expertise_name': Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'class_level_name' in self.fields:
            self.fields['class_level_name'].queryset = self.fields['class_level_name'].queryset.order_by('serial')

        # Add the 'form-control' class to all fields except checkboxes
        for field_name, field in self.fields.items():
            widget = field.widget
            if not isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-control'



from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})



