from django import forms
from django import forms
from django import forms
from .models import RequestHistory
from django_select2.forms import Select2Widget
from users.models import Expertise
from .models import RequestHistory
from django_select2.forms import Select2Widget
from django.forms import NumberInput
import datetime
from django.forms import TimeInput
from django import forms
from .models import RequestHistory
from datetime import datetime
from dateutil import parser
from django_select2.forms import Select2Widget


# class FindExpertForm(forms.ModelForm):
#     preferred_date = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date',}),
#         required=True
#     )
#     preferred_time_input = forms.CharField(
#         widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control border'}),
#         required=True
#     )

#     class Meta:
#         model = RequestHistory
#         fields = [
#             'expertise_name', 'duration', 'class_level_name', 'language', 
#             'gender', 'note', 'amount'
#         ]
#         widgets = {
#             'expertise_name': Select2Widget,
#             'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         if 'expertise_name' in self.fields:
#             self.fields['expertise_name'].required = True
            
#         if 'class_level_name' in self.fields:
#             self.fields['class_level_name'].queryset = self.fields['class_level_name'].queryset.order_by('serial')
#             self.fields['class_level_name'].required = True
        
#         # Apply form-control class to all fields
#         for field in self.fields.values():
#             field.widget.attrs.setdefault('class', 'form-control')

#     def clean(self):
#         cleaned_data = super().clean()
#         preferred_date = cleaned_data.get('preferred_date')
#         preferred_time_input = cleaned_data.get('preferred_time_input')
        
#         if preferred_date:
#             try:
#                 preferred_time = parser.parse(preferred_time_input).time() if preferred_time_input else datetime.min.time()
#                 cleaned_data['preferred_time'] = datetime.combine(preferred_date, preferred_time)
#             except ValueError:
#                 raise forms.ValidationError("Invalid time format. Please enter a valid time.")
        
#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.preferred_time = self.cleaned_data.get('preferred_time')
#         if commit:
#             instance.save()
#         return instance

# class BrowseExpertForm(forms.ModelForm):
#     preferred_date = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date',}),
#         required=True
#     )
#     preferred_time_input = forms.CharField(
#         widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control border'}),
#         required=True
#     )
    
#     class Meta:
#         model = RequestHistory
#         fields = [
#             'expertise_name', 'duration', 'class_level_name', 'language', 
#             'gender', 'note',
#         ]
#         widgets = {
#             'expertise_name': Select2Widget,
#             'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         if 'expertise_name' in self.fields:
#             self.fields['expertise_name'].required = True
            
#         if 'class_level_name' in self.fields:
#             self.fields['class_level_name'].queryset = self.fields['class_level_name'].queryset.order_by('serial')
#             self.fields['class_level_name'].required = True
            
#         # Apply form-control class to all fields
#         for field in self.fields.values():
#             field.widget.attrs.setdefault('class', 'form-control')

#     def clean(self):
#         cleaned_data = super().clean()
#         preferred_date = cleaned_data.get('preferred_date')
#         preferred_time_input = cleaned_data.get('preferred_time_input')
        
#         if preferred_date:
#             try:
#                 preferred_time = parser.parse(preferred_time_input).time() if preferred_time_input else datetime.min.time()
#                 cleaned_data['preferred_time'] = datetime.combine(preferred_date, preferred_time)
#             except ValueError:
#                 raise forms.ValidationError("Invalid time format. Please enter a valid time.")
        
#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.preferred_time = self.cleaned_data.get('preferred_time')
#         if commit:
#             instance.save()
#         return instance


class FindBrowseExpertForm(forms.ModelForm):
    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        initial=datetime.today
    )
    preferred_time_input = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control border'}),
        required=True
    )

    class Meta:
        model = RequestHistory
        fields = [
            'expertise_name', 'duration', 'class_level_name', 'language', 
            'gender', 'note', 'amount'
        ]
        widgets = {
            'expertise_name': Select2Widget,
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'expertise_name' in self.fields:
            self.fields['expertise_name'].required = True

        if 'class_level_name' in self.fields:
            self.fields['class_level_name'].queryset = self.fields['class_level_name'].queryset.order_by('serial')
            self.fields['class_level_name'].required = True
        
        # Apply form-control class to all fields
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        preferred_date = cleaned_data.get('preferred_date')
        preferred_time_input = cleaned_data.get('preferred_time_input')

        if preferred_date:
            try:
                preferred_time = parser.parse(preferred_time_input).time() if preferred_time_input else datetime.min.time()
                cleaned_data['preferred_time'] = datetime.combine(preferred_date, preferred_time)
            except ValueError:
                raise forms.ValidationError("Invalid time format. Please enter a valid time.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.preferred_time = self.cleaned_data.get('preferred_time')
        if commit:
            instance.save()
        return instance


