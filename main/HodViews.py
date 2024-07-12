from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from  main.models import CustomUser, Staffs, Courses, Students, Location
from .forms import AddStudentForm, EditStudentForm
import re
from django.utils.dateparse import parse_datetime
from django.utils import timezone




def admin_home(request):
    all_student_count = Students.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    student_count_list_in_course = []

    for course in course_all:
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        student_count_list_in_course.append(students)
    
    student_count_list_in_subject = []

    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        student_attendance_present_list.append(attendance)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "student_count_list_in_course": student_count_list_in_course,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)





def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")



def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            # Creating the user
            user = CustomUser.objects.create_user(
                username=username, 
                password=password, 
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                user_type=2
            )

            # Creating the staff profile
            staff = Staffs(admin=user, address=address)
            staff.save()

            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
            return redirect('add_staff')
        except Exception as e:
            messages.error(request, f"Failed to Add Staff: {e}")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')



def add_course(request):
    staff_list = Staffs.objects.all()
    if not staff_list.exists():
        messages.error(request, "No staff found in the database")
    context = {
        'staff_list': staff_list
    }
    return render(request, "hod_template/add_course_template.html", context)

def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course_name = request.POST.get('course')
        staff_id = request.POST.get('staff')  # Retrieve the staff ID from the form

        try:
            staff_instance = Staffs.objects.get(id=staff_id)  # Retrieve the staff instance
            course_model = Courses(course_name=course_name, staff=staff_instance)  # Associate staff with course
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except Staffs.DoesNotExist:
            messages.error(request, "Selected staff does not exist!")
            return redirect('add_course')
        except Exception as e:
            messages.error(request, f"Failed to Add Course! Error: {str(e)}")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')



def add_student(request):
    form = AddStudentForm()
    context = {
        'form': form,
        'gender_list': form.fields['gender'].choices,  # Pass gender choices to the template
        'course_choices': form.fields['course_id'].choices,  # Pass course choices to the template
    }
    return render(request, 'hod_template/add_student_template.html', context)


def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']

            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=3
                )

                course = Courses.objects.get(id=course_id)

                student_model = Students(
                    admin=user,
                    address=address,
                    course=course,  # Use 'course' instead of 'course_id'
                    gender=gender,
                    profile_pic=profile_pic_url
                )
                student_model.save()

                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except Exception as e:
                messages.error(request, f"Failed to Add Student: {e}")
                return redirect('add_student')
        else:
            messages.error(request, "Form is not valid")
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Students
from .forms import EditStudentForm  # Assuming you have a form defined for editing students

def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    # Retrieve the student object
    student = get_object_or_404(Students, admin_id=student_id)

    # Initialize the form with initial data
    form = EditStudentForm(initial={
        'email': student.admin.email,
        'username': student.admin.username,
        'first_name': student.admin.first_name,
        'last_name': student.admin.last_name,
        'address': student.address,
        'gender': student.gender,
        'course_id': student.course_id,  # Assuming course_id is the correct field to access the course ID
    })

    context = {
        'id': student_id,
        'username': student.admin.username,
        'form': form,
    }

    return render(request, 'hod_template/edit_student_template.html', context)

def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if not student_id:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']

            try:
                # Profile Pic Handling
                if 'profile_pic' in request.FILES:
                    profile_pic = request.FILES['profile_pic']
                    fs = FileSystemStorage()
                    filename = fs.save(profile_pic.name, profile_pic)
                    profile_pic_url = fs.url(filename)
                else:
                    profile_pic_url = None

                # Update Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address
                student_model.course_id_id = course_id
                student_model.gender = gender
                if profile_pic_url:
                    student_model.profile_pic = profile_pic_url
                student_model.save()

                # Clear session
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+str(student_id))
            except Exception as e:
                messages.error(request, "Failed to Update Student: " + str(e))
                return redirect('/edit_student/'+str(student_id))
        else:
            messages.error(request, "Form is not valid")
            return redirect('/edit_student/'+str(student_id))


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')





def add_location(request):
    student_list = Students.objects.all()
    if not student_list.exists():
        messages.error(request, "No students found in the database")
    context = {
        'student_list': student_list
    }
    return render(request, "hod_template/add_location_template.html", context)

def add_location_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_location')
    else:
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        student_id = request.POST.get('student')

        try:
            student_instance = Students.objects.get(id=student_id)
            location_model = Location(latitude=latitude, longitude=longitude, student=student_instance)
            location_model.save()
            messages.success(request, "Location Added Successfully!")
            return redirect('add_location')
        except Students.DoesNotExist:
            messages.error(request, "Selected student does not exist!")
            return redirect('add_location')
        except Exception as e:
            messages.error(request, f"Failed to Add Location! Error: {str(e)}")
            return redirect('add_location')


def manage_location(request):
    locations = Location.objects.select_related('student').all()
    context = {
        "locations": locations
    }
    return render(request, 'hod_template/manage_location_template.html', context)

def edit_location(request, location_id):
    location = Location.objects.get(id=location_id)
    student_list = Students.objects.all()
    context = {
        "location": location,
        "student_list": student_list,
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
        student_id = request.POST.get('student')

        try:
            location = Location.objects.get(id=location_id)
            location.latitude = latitude
            location.longitude = longitude
            student_instance = Students.objects.get(id=student_id)
            location.student = student_instance
            location.save()

            messages.success(request, "Location Updated Successfully.")
            return redirect('/edit_location/' + location_id)

        except Students.DoesNotExist:
            messages.error(request, "Selected student does not exist!")
            return redirect('/edit_location/' + location_id)
        except Exception as e:
            messages.error(request, f"Failed to Update Location! Error: {str(e)}")
            return redirect('/edit_location/' + location_id)

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
            student = Students.objects.get(id=student_id)

            # Create the Location instance, using the current time if timestamp is not provided
            location = Location(
                student=student,
                latitude=latitude,
                longitude=longitude,
                timestamp=parse_datetime(timestamp) if timestamp else timezone.now()
            )
            location.save()

            return JsonResponse({"status": "success", "message": "Location data saved successfully"})
        except Students.DoesNotExist:
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



def admin_view_attendance(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses,
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    course_id = request.POST.get("course")
    

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    course_model = Courses.objects.get(id=course_id)

    

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=course_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "course_id":attendance_single.course_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


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
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass




def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")




