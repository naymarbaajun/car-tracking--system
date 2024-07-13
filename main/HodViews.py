from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .models import CustomUser, AdminHOD, Cars, Owners, Location
from .forms import AddOwnerForm, EditOwnerForm
from django.utils.dateparse import parse_datetime
from django.utils import timezone

def admin_home(request):
    all_owner_count = Owners.objects.all().count()
    car_count = Cars.objects.all().count()

    # Total Cars and owners in Each Car
    car_all = Cars.objects.all()
    car_name_list = []
    owner_count_list_in_car = []

    for car in car_all:
        owners = Owners.objects.filter(car_id=car.id).count()
        car_name_list.append(car.car_name)
        owner_count_list_in_car.append(owners)
    
    owner_name_list = []

    owners = Owners.objects.all()
    for owner in owners:
        owner_name_list.append(owner.first_name)
    
    locations = Location.objects.all()

    context = {
        "all_owner_count": all_owner_count,
        "car_count": car_count,
        "car_name_list": car_name_list,
        "owner_count_list_in_car": owner_count_list_in_car,
        "owner_name_list": owner_name_list,
        "locations": locations,
    }
    return render(request, "hod_template/home_content.html", context)

def add_car(request):
    if request.method == "POST":
        car_name = request.POST.get('car_name')
        car_color = request.POST.get('car_color')
        car_model = request.POST.get('car_model')
        year = request.POST.get('year')

        try:
            car_model = Cars(car_name=car_name, car_color=car_color, car_model=car_model, year=year)
            car_model.save()
            messages.success(request, "Car Added Successfully!")
            return redirect('add_car')
        except Exception as e:
            messages.error(request, f"Failed to Add Car! Error: {str(e)}")
            return redirect('add_car')
    else:
        return render(request, "hod_template/add_car_template.html", {})
    

def manage_car(request):
    cars = Cars.objects.all()
    owners = Owners.objects.all()  # Fetch all owners
    
    context = {
        'cars': cars,
        'owners': owners,  # Include owners in the context
    }
    return render(request, 'hod_template/manage_car_template.html', context)



def edit_car(request, car_id):
    try:
        car = Cars.objects.get(id=car_id)
        context = {
            "car": car,
            "id": car_id
        }
        if request.method == "POST":
            car.car_name = request.POST.get('car_name')
            car.car_color = request.POST.get('car_color')
            car.car_model = request.POST.get('car_model')
            car.year = request.POST.get('year')
            car.save()
            messages.success(request, "Car Updated Successfully.")
            return redirect('edit_car', car_id=car_id)
        return render(request, 'hod_template/edit_car_template.html', context)
    except Cars.DoesNotExist:
        messages.error(request, "Car not found.")
        return redirect('manage_car')
    except Exception as e:
        messages.error(request, f"Failed to Update Car: {str(e)}")
        return redirect('manage_car')

def delete_car(request, car_id):
    try:
        car = Cars.objects.get(id=car_id)
        car.delete()
        messages.success(request, "Car Deleted Successfully.")
    except Cars.DoesNotExist:
        messages.error(request, "Car not found.")
    except Exception as e:
        messages.error(request, f"Failed to Delete Car: {str(e)}")
    return redirect('manage_car')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from main.models import Owners, Cars
from .forms import AddOwnerForm

def add_owner(request):
    form = AddOwnerForm()
    context = {
        'form': form,
        'gender_list': form.fields['gender'].choices,
    }
    return render(request, 'hod_template/add_owner_template.html', context)

def add_owner_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_owner')
    else:
        form = AddOwnerForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']

            if 'owner_picture' in request.FILES:
                owner_picture = request.FILES['owner_picture']
                fs = FileSystemStorage()
                filename = fs.save(owner_picture.name, owner_picture)
                owner_picture_url = fs.url(filename)
            else:
                owner_picture_url = form.cleaned_data['owner_picture']  # Use default value if not provided

            try:
                owner_model = Owners(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    phone_number=phone_number,
                    address=address,
                    owner_picture=owner_picture_url
                )
                owner_model.save()

                messages.success(request, "Owner Added Successfully!")
                return redirect('add_owner')
            except Exception as e:
                messages.error(request, f"Failed to Add Owner: {e}")
                return redirect('add_owner')
        else:
            messages.error(request, "Form is not valid")
            return redirect('add_owner')


def manage_owner(request):
    owners = Owners.objects.all()
    context = {
        "owners": owners
    }
    return render(request, 'hod_template/manage_owner_template.html', context)

def edit_owner(request, owner_id):
    request.session['owner_id'] = owner_id
    owner = get_object_or_404(Owners, id=owner_id)

    form = EditOwnerForm(initial={
        'email': owner.email,
        'first_name': owner.first_name,
        'last_name': owner.last_name,
        'address': owner.address,
        'gender': owner.gender,
        'phone_number': owner.phone_number,
        'owner_picture': owner.owner_picture,
    })

    context = {
        'id': owner_id,
        'form': form,
    }

    return render(request, 'hod_template/edit_owner_template.html', context)

def edit_owner_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        owner_id = request.session.get('owner_id')
        if not owner_id:
            return redirect('/manage_owner')

        form = EditOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            phone_number = form.cleaned_data['phone_number']
            gender = form.cleaned_data['gender']

            try:
                if 'owner_picture' in request.FILES:
                    owner_picture = request.FILES['owner_picture']
                    fs = FileSystemStorage()
                    filename = fs.save(owner_picture.name, owner_picture)
                    owner_picture_url = fs.url(filename)
                else:
                    owner_picture_url = None

                owner_model = Owners.objects.get(id=owner_id)
                owner_model.email = email
                owner_model.first_name = first_name
                owner_model.last_name = last_name
                owner_model.address = address
                owner_model.phone_number = phone_number
                owner_model.gender = gender
                if owner_picture_url:
                    owner_model.owner_picture = owner_picture_url
                owner_model.save()

                del request.session['owner_id']

                messages.success(request, "Owner Updated Successfully!")
                return redirect('/edit_owner/'+str(owner_id))
            except Exception as e:
                messages.error(request, "Failed to Update Owner: " + str(e))
                return redirect('/edit_owner/'+str(owner_id))
        else:
            messages.error(request, "Form is not valid")
            return redirect('/edit_owner/'+str(owner_id))

def delete_owner(request, owner_id):
    owner = get_object_or_404(Owners, id=owner_id)
    try:
        owner.delete()
        messages.success(request, "Owner Deleted Successfully.")
        return redirect('manage_owner')
    except Exception as e:
        messages.error(request, "Failed to Delete Owner: " + str(e))
        return redirect('manage_owner')

def add_location(request):
    owner_list = Owners.objects.all()
    if not owner_list.exists():
        messages.error(request, "No owners found in the database")
    context = {
        'owner_list': owner_list
    }
    return render(request, "hod_template/add_location_template.html", context)

def add_location_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_location')
    
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    owner_id = request.POST.get('owner')
    timestamp_str = request.POST.get('timestamp')

    try:
        timestamp = parse_datetime(timestamp_str)
        if timestamp is None:
            raise ValueError("Invalid timestamp format")

        owner = Owners.objects.get(id=owner_id)

        location = Location(
            latitude=latitude,
            longitude=longitude,
            owner=owner,
            timestamp=timestamp
        )
        location.save()
        messages.success(request, "Location Added Successfully!")
        return redirect('add_location')
    except Exception as e:
        messages.error(request, f"Failed to Add Location: {e}")
        return redirect('add_location')

def manage_location(request):
    locations = Location.objects.all()
    context = {
        "locations": locations
    }
    return render(request, 'hod_template/manage_location_template.html', context)

def edit_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    context = {
        "location": location,
        "id": location_id
    }
    return render(request, 'hod_template/edit_location_template.html', context)

def edit_location_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        location_id = request.POST.get('location_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        owner_id = request.POST.get('owner_id')
        timestamp_str = request.POST.get('timestamp')

        try:
            timestamp = parse_datetime(timestamp_str)
            if timestamp is None:
                raise ValueError("Invalid timestamp format")

            location = Location.objects.get(id=location_id)
            location.latitude = latitude
            location.longitude = longitude
            location.owner_id = owner_id
            location.timestamp = timestamp
            location.save()

            messages.success(request, "Location Updated Successfully.")
            return redirect('/edit_location/'+location_id)

        except Exception as e:
            messages.error(request, f"Failed to Update Location: {e}")
            return redirect('/edit_location/'+location_id)

def delete_location(request, location_id):
    location = Location.objects.get(id=location_id)
    try:
        location.delete()
        messages.success(request, "Location Deleted Successfully.")
        return redirect('manage_location')
    except:
        messages.error(request, "Failed to Delete Location.")
        return redirect('manage_location')





@csrf_exempt
def receive_location_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            student_id = data.get('student_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            timestamp = data.get('timestamp', None)

            # Ensure all required fields are provided
            if not all([student_id, latitude, longitude]):
                return JsonResponse({"status": "error", "message": "Missing required fields"})

            # Find the student instance
            student = Owners.objects.get(id=student_id)

            # Create the Location instance, using the current time if timestamp is not provided
            location = Location(
                student=student,
                latitude=latitude,
                longitude=longitude,
                timestamp=parse_datetime(timestamp) if timestamp else timezone.now()
            )
            location.save()

            return JsonResponse({"status": "success", "message": "Location data saved successfully"})
        except Owners.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student not found"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})



@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)





def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    





