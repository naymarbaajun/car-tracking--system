from django import forms
from main.models import Owners, Cars

class DateInput(forms.DateInput):
    input_type = "date"

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

class AddOwnerForm(forms.ModelForm):
    class Meta:
        model = Owners
        fields = [
            'email', 
            'first_name', 
            'last_name', 
            'gender', 
            'phone_number', 
            'address', 
            'owner_picture', 
        
        ]
        widgets = {
            'email': forms.EmailInput(attrs={"class":"form-control"}),
            'first_name': forms.TextInput(attrs={"class":"form-control"}),
            'last_name': forms.TextInput(attrs={"class":"form-control"}),
            'gender': forms.Select(choices=GENDER_CHOICES, attrs={"class":"form-control"}),
            'phone_number': forms.TextInput(attrs={"class":"form-control"}),
            'address': forms.TextInput(attrs={"class":"form-control"}),
            'owner_picture': forms.FileInput(attrs={"class":"form-control"}),
         
        }

class EditOwnerForm(forms.ModelForm):
    class Meta:
        model = Owners
        fields = [
            'email', 
            'first_name', 
            'last_name', 
            'gender', 
            'phone_number', 
            'address', 
            'owner_picture', 
 
        ]
        widgets = {
            'email': forms.EmailInput(attrs={"class": "form-control"}),
            'first_name': forms.TextInput(attrs={"class": "form-control"}),
            'last_name': forms.TextInput(attrs={"class": "form-control"}),
            'gender': forms.Select(choices=GENDER_CHOICES, attrs={"class": "form-control"}),
            'phone_number': forms.TextInput(attrs={"class": "form-control"}),
            'address': forms.TextInput(attrs={"class": "form-control"}),
            'owner_picture': forms.FileInput(attrs={"class": "form-control"}),
       
        }
