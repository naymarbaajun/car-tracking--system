from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .models import CustomUser, AdminHOD, Cars, Owners, CarboxDetail
from .forms import AddOwnerForm, EditOwnerForm
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth import get_user_model 




def admin_home(request):
    # Counting objects
    all_owner_count = Owners.objects.all().count()
    car_count = Cars.objects.all().count()
    carbox_detail_count = CarboxDetail.objects.all().count()

    # Getting car details
    car_all = Cars.objects.all()
    car_name_list = []
    owner_count_list_in_car = []

    for car in car_all:
        owners = Owners.objects.filter(id=car.owner.id).count()  # Corrected line
        car_name_list.append(car.car_name)
        owner_count_list_in_car.append(owners)
    
    # Getting owner details
    owner_name_list = []
    owners = Owners.objects.all()
    for owner in owners:
        owner_name_list.append(owner.first_name)
    
    # Getting carbox details
    carbox_details = CarboxDetail.objects.all()

    context = {
        "all_owner_count": all_owner_count,
        "car_count": car_count,
        "carbox_detail_count": carbox_detail_count,
        "car_name_list": car_name_list,
        "owner_count_list_in_car": owner_count_list_in_car,
        "owner_name_list": owner_name_list,
        "carbox_details": carbox_details,
    }
    return render(request, "hod_template/home_content.html", context)


def add_car(request):
    if request.method == "POST":
        car_name = request.POST.get('car_name')
        car_color = request.POST.get('car_color')
        car_model = request.POST.get('car_model')
        year = request.POST.get('year')
        owner_id = request.POST.get('owner')  # Fetch owner ID from form

        try:
            # Retrieve the owner object using the owner_id
            owner = Owners.objects.get(id=owner_id)
            
            # Create a new Cars object with owner assigned
            car_model = Cars(car_name=car_name, car_color=car_color, car_model=car_model, year=year, owner=owner)
            car_model.save()
            
            messages.success(request, "Car Added Successfully!")
            return redirect('add_car')
        except Owners.DoesNotExist:
            messages.error(request, "Owner not found.")
        except Exception as e:
            messages.error(request, f"Failed to Add Car! Error: {str(e)}")
        
        return redirect('add_car')
    else:
        owners = Owners.objects.all()  # Fetch all owners to populate the select dropdown
        context = {
            'owners': owners,
        }
        return render(request, "hod_template/add_car_template.html", context)


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
        form = AddOwnerForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Owner Added Successfully!")
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
    owner = get_object_or_404(Owners, id=owner_id)

    form = EditOwnerForm(instance=owner)

    context = {
        'id': owner_id,
        'form': form,
    }

    return render(request, 'hod_template/edit_owner_template.html', context)

def edit_owner_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        owner_id = request.POST.get('owner_id')
        if not owner_id:
            return redirect('/manage_owner')

        owner = get_object_or_404(Owners, id=owner_id)
        form = EditOwnerForm(request.POST, instance=owner)

        if form.is_valid():
            form.save()
            messages.success(request, "Owner Updated Successfully!")
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
    


def add_carbox_detail(request):
    owner_list = Owners.objects.all()
    if not owner_list.exists():
        messages.error(request, "No owners found in the database")
    context = {
        'owner_list': owner_list
    }
    return render(request, "hod_template/add_carbox_detail_template.html", context)

def add_carbox_detail_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_carbox_detail')
    
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    owner_id = request.POST.get('owner')
    car_id = request.POST.get('car')
    timestamp_str = request.POST.get('timestamp')
    left_indicator_status = request.POST.get('left_indicator_status') == 'on'
    right_indicator_status = request.POST.get('right_indicator_status') == 'on'
    alcohol_detected = request.POST.get('alcohol_detected') == 'on'
    vibration = request.POST.get('vibration') == 'on'
    headlight_status = request.POST.get('headlight_status') == 'on'
    hazard_status = request.POST.get('hazard_status') == 'on'

    try:
        timestamp = parse_datetime(timestamp_str)
        if timestamp is None:
            raise ValueError("Invalid timestamp format")

        owner = Owners.objects.get(id=owner_id)
        car = Cars.objects.get(id=car_id)

        carbox_detail = CarboxDetail(
            latitude=latitude,
            longitude=longitude,
            owner=owner,
            car=car,
            timestamp=timestamp,
            left_indicator_status=left_indicator_status,
            right_indicator_status=right_indicator_status,
            alcohol_detected=alcohol_detected,
            vibration=vibration,
            headlight_status=headlight_status,
            hazard_status=hazard_status
        )
        carbox_detail.save()
        messages.success(request, "Carbox Detail Added Successfully!")
        return redirect('add_carbox_detail')
    except Exception as e:
        messages.error(request, f"Failed to Add Carbox Detail: {e}")
        return redirect('add_carbox_detail')

def manage_carbox_detail(request):
    carbox_details = CarboxDetail.objects.all()
    context = {
        "carbox_details": carbox_details
    }
    return render(request, 'hod_template/manage_carbox_detail_template.html', context)

def edit_carbox_detail(request, carbox_detail_id):
    carbox_detail = get_object_or_404(CarboxDetail, id=carbox_detail_id)
    context = {
        "carbox_detail": carbox_detail,
        "id": carbox_detail_id
    }
    return render(request, 'hod_template/edit_carbox_detail_template.html', context)


def edit_carbox_detail_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        carbox_detail_id = request.POST.get('carbox_detail_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        owner_id = request.POST.get('owner_id')
        car_id = request.POST.get('car_id')
        timestamp_str = request.POST.get('timestamp')
        left_indicator_status = request.POST.get('left_indicator_status') == 'on'
        right_indicator_status = request.POST.get('right_indicator_status') == 'on'
        alcohol_detected = request.POST.get('alcohol_detected') == 'on'
        vibration = request.POST.get('vibration') == 'on'
        headlight_status = request.POST.get('headlight_status') == 'on'
        hazard_status = request.POST.get('hazard_status') == 'on'

        try:
            timestamp = parse_datetime(timestamp_str)
            if timestamp is None:
                raise ValueError("Invalid timestamp format")

            carbox_detail = CarboxDetail.objects.get(id=carbox_detail_id)
            carbox_detail.latitude = latitude
            carbox_detail.longitude = longitude
            carbox_detail.owner_id = owner_id
            carbox_detail.car_id = car_id
            carbox_detail.timestamp = timestamp
            carbox_detail.left_indicator_status = left_indicator_status
            carbox_detail.right_indicator_status = right_indicator_status
            carbox_detail.alcohol_detected = alcohol_detected
            carbox_detail.vibration = vibration
            carbox_detail.headlight_status = headlight_status
            carbox_detail.hazard_status = hazard_status
            carbox_detail.save()

            messages.success(request, "Carbox Detail Updated Successfully.")
            return redirect(f'/edit_carbox_detail/{carbox_detail_id}')

        except Exception as e:
            messages.error(request, f"Failed to Update Carbox Detail: {e}")
            return redirect(f'/edit_carbox_detail/{carbox_detail_id}')

def delete_carbox_detail(request, carbox_detail_id):
    carbox_detail = CarboxDetail.objects.get(id=carbox_detail_id)
    try:
        carbox_detail.delete()
        messages.success(request, "Carbox Detail Deleted Successfully.")
        return redirect('manage_carbox_detail')
    except:
        messages.error(request, "Failed to Delete Carbox Detail.")
        return redirect('manage_carbox_detail')
    




def view_carbox_location(request, car_id):
    # Assuming you have a method to identify the current user's related car
    # For example, request.user.customuser.car or similar method to get car details
    car = get_object_or_404(Cars, id=car_id)
    carbox_location = CarboxDetail.objects.filter(car=car).order_by('-timestamp').first()
    
    if carbox_location is None:
        context = {
            'error': 'No carbox location found for this car'
        }
    else:
        context = {
            'carbox_location': carbox_location
        }

    return render(request, 'hod_template/carbox_location_template.html', context)



@csrf_exempt
def receive_carbox_detail_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            owner_id = data.get('owner_id')
            car_id = data.get('car_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            timestamp = data.get('timestamp', None)
            left_indicator_status = data.get('left_indicator_status', False)
            right_indicator_status = data.get('right_indicator_status', False)
            alcohol_detected = data.get('alcohol_detected', False)
            vibration = data.get('vibration', False)
            headlight_status = data.get('headlight_status', False)
            hazard_status = data.get('hazard_status', False)

            # Ensure all required fields are provided
            if not all([owner_id, car_id, latitude, longitude]):
                return JsonResponse({"status": "error", "message": "Missing required fields"})

            # Find the owner and car instances
            owner = Owners.objects.get(id=owner_id)
            car = Cars.objects.get(id=car_id)

            # Create the CarboxDetail instance, using the current time if timestamp is not provided
            carbox_detail = CarboxDetail(
                owner=owner,
                car=car,
                latitude=latitude,
                longitude=longitude,
                timestamp=parse_datetime(timestamp) if timestamp else timezone.now(),
                left_indicator_status=left_indicator_status,
                right_indicator_status=right_indicator_status,
                alcohol_detected=alcohol_detected,
                vibration=vibration,
                headlight_status=headlight_status,
                hazard_status=hazard_status
            )
            carbox_detail.save()

            return JsonResponse({"status": "success", "message": "Carbox detail data saved successfully"})
        except Owners.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Owner not found"})
        except Cars.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Car not found"})
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
    





