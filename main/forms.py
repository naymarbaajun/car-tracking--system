from django import forms
from django.forms import Form
from main.models import Cars

class DateInput(forms.DateInput):
    input_type = "date"

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

class AddOwnerForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddOwnerForm, self).__init__(*args, **kwargs)
        self.fields['car_id'] = forms.ChoiceField(
            label="Car", 
            choices=self.get_car_choices(), 
            widget=forms.Select(attrs={"class":"form-control"})
        )
        self.fields['gender'] = forms.ChoiceField(
            label="Gender", 
            choices=GENDER_CHOICES, 
            widget=forms.Select(attrs={"class":"form-control"})
        )
        self.fields['profile_pic'] = forms.FileField(
            label="Profile Pic", 
            required=False, 
            widget=forms.FileInput(attrs={"class":"form-control"})
        )

    def get_car_choices(self):
        try:
            cars = Cars.objects.all()
            return [(car.id, car.car_name) for car in cars]
        except:
            return []


class EditOwnerForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    profile_pic = forms.FileField(label="Profile Pic", required=False, widget=forms.FileInput(attrs={"class": "form-control"}))
    car_id = forms.ChoiceField(label="Car", choices=[], widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super(EditOwnerForm, self).__init__(*args, **kwargs)
        try:
            cars = Cars.objects.all()
            self.fields['car_id'].choices = [(car.id, car.car_name) for car in cars]
        except:
            pass