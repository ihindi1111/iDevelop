from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.dispatch import receiver
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from idevelop.models import Student, Profile, CollabBox
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.signals import user_logged_in
from .models import Student, FriendRequest
from django.shortcuts import get_object_or_404
from idevelop.forms import RegisterForm, StudentForm

#New to replace oauth:
from django.contrib.auth.forms import AuthenticationForm



################################# Google oAuth #################################
def home(request):
    return render(request, 'welcome.html')

def home_action(request):
    return redirect("register-action")


################################################################################
#Note Might Have to also create the student account and add parameters to the form
def register_action(request):
    if request.method == 'POST':
        post_data = request.POST
        form = RegisterForm(post_data)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            authenticated_user = authenticate(
                username=user.username, password=form.cleaned_data['password1']
            )
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('post-welcome')
            else:
                return render(request, 'register.html', {
                    'form': form,
                    'error': "Unexpected error: Unable to authenticate user."
                })
        else:
            return render(request, 'register.html', {'form': form})
    
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_action(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            try:
                request.user.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=request.user)
            try: 
                 CollabBox.objects.filter(owner=request.user)
            except CollabBox.DoesNotExist:
                collabBox = CollabBox.objects.create(owner = user)
                collabBox.save()
            return redirect('post-welcome')
        else:
            return render(request, 'login.html', {'form': form})

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def validate_register_form(post_data):
    """Custom function to validate the registration form data."""
    errors = {}

    username = post_data.get('username')
    if not username:
        errors['username'] = "Username is required."
    elif User.objects.filter(username__iexact=username).exists():
        errors['username'] = "Username is already taken."
    
    return errors
    
def _my_json_error_response(message, status=200):
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)


def post_welcome(request):
    current_user = request.user
    print(f"Current user: {current_user.username}")
    # Ensure the Student profile exists for the current user
    try:
        student = Student.objects.get(user=current_user)
    except:
        student = Student.objects.create(user=current_user)
    
    owned_collab_box = current_user.owned_collab_boxes.first()
    print(f"Existing CollabBox: {owned_collab_box}")
    if not owned_collab_box:
        owned_collab_box = CollabBox.objects.create(owner=current_user)
        print(f"Created new CollabBox: {owned_collab_box}")
    owned_id = owned_collab_box.id
    print(f"Owned Box ID: {owned_id}")

    friend_profiles = student.friends.all()
    print(f"Set of Friends: {friend_profiles}")
    user_collab_dict = {
        profile: profile.user.owned_collab_boxes.first().id if profile.user.owned_collab_boxes.exists() else None
        for profile in friend_profiles
    }

    context = {'following_profiles': friend_profiles, 'owned_box_ID': owned_id, 'user_collab_dict':user_collab_dict, 'user': current_user}

    return render(request, 'post-welcome.html', context)

def credits(request):
    context = {
    }
    return render(request, 'credits.html', context)


def settings(request):
    context = {
    }
    return render(request, 'settings.html', context)

def materials(request):
    context = {
    }
    return render(request, 'materials.html', context)

def profile(request, user_id):
    user = User.objects.get(id=user_id)
    curr_user = request.user
    is_you = curr_user == user

    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        student = Student.objects.create(user=user)

    # Handle form submission
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user.id)
    else:
        form = StudentForm(instance=student)

    # Get the user's friends
    friends = student.friends.all()
    if curr_user.student_profile in friends:
        is_friend = True
    else:
        is_friend = False
    collab_box = curr_user.owned_collab_boxes.first()
    if not collab_box:
        collab_box = CollabBox.objects.create(owner=curr_user)

    if collab_box.allowed_editors.filter(id=user.id).exists():
        is_permitted = True
    else:
        is_permitted = False

    # Render the profile page with the form and additional context
    return render(request, 'profile.html', {
        'form': form,
        'profile_user': user,
        'is_you': is_you,
        'friends': friends,
        'is_permitted': is_permitted,
        'is_friend': is_friend,
    })

def permit_edits(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id = user_id)
        current_user = request.user
        collab_box = current_user.owned_collab_boxes.first()
        if not collab_box:
            collab_box = CollabBox.objects.create(owner=current_user)
        collab_box.allowed_editors.add(user)
        return redirect("profile", user_id = user_id)

def prevent_edits(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        current_user = request.user
        collab_box = current_user.owned_collab_boxes.first()
        if not collab_box:
            return redirect("profile", user_id=user_id)  # No collab box exists
        collab_box.allowed_editors.remove(user)
        return redirect("profile", user_id=user_id)
    
def lesson1(request):
    student = request.user.student_profile
    if request.method == 'POST':
        code = request.POST.get('code')
        lesson = 'lesson1'
        student.code_storage[lesson] = code
        student.save()
        return HttpResponse(status=204)  # Send an empty response to indicate success

    # Load the saved code if it exists
    saved_code = student.code_storage.get('lesson1', '')
    context = {
                "answers": student.answers,
                "saved_code": saved_code
            }
    return render(request, 'lesson1.html', context)

def lesson2(request):
    student = request.user.student_profile
    if request.method == 'POST':
        code = request.POST.get('code')
        lesson = 'lesson2'
        student.code_storage[lesson] = code
        student.save()
        return HttpResponse(status=204)  # Send an empty response to indicate success

    # Load the saved code if it exists
    saved_code = student.code_storage.get('lesson2', '')
    context = {
                "answers": student.answers,
                "saved_code": saved_code
            }
    return render(request, 'lesson2.html', context)

def lesson3(request):
    student = request.user.student_profile
    if request.method == 'POST':
        code = request.POST.get('code')
        lesson = 'lesson3'
        student.code_storage[lesson] = code
        student.save()
        return HttpResponse(status=204)  # Send an empty response to indicate success

    # Load the saved code if it exists
    saved_code = student.code_storage.get('lesson3', '')
    context = {
                "answers": student.answers,
                "saved_code": saved_code
            }
    return render(request, 'lesson3.html', context)

def submit_answer_1(request, lesson, question):
    if request.method == "POST":
        answer = request.POST.get('answer')

        student = request.user.student_profile

        if check_answer_1(question, answer):
            print(student.answers)
            if f"{lesson}" not in student.answers:
                student.answers[f"{lesson}"] = {}
            if f"{question}" not in student.answers[f"{lesson}"]:
                print(student.answers)
                d = {f"{question}" : answer}
                student.answers[f"{lesson}"].update(d)
                print(student.answers)
                student.save()
            context = {
                "answers": student.answers
            }
            return render(request, 'lesson1.html', context)
        else:
            return HttpResponse("invalid", status = 304)

def check_answer_1(question, answer):
    correct_answers = {
        1: '<!DOCTYPE html>',
        2: '.red-bold { color: red; font-weight: bold; }'
    }
    return answer == correct_answers.get(question, "")

def submit_answer_2(request, lesson, question):
    if request.method == "POST":
        answer = request.POST.get('answer')

        student = request.user.student_profile

        if check_answer_2(question, answer):
            print(student.answers)
            if f"{lesson}" not in student.answers:
                student.answers[f"{lesson}"] = {}
            if f"{question}" not in student.answers[f"{lesson}"]:
                print(student.answers)
                d = {f"{question}" : answer}
                student.answers[f"{lesson}"].update(d)
                print(student.answers)
                student.save()
            context = {
                "answers": student.answers
            }
            return render(request, 'lesson2.html', context)
        else:
            return HttpResponse("invalid", status = 304)
        
def check_answer_2(question, answer):
    correct_answers = {
        1: '<p style="font-weight: bold; font-style: italic;">',
        2: '.red-bold { color: red; font-weight: bold; font-family: Arial}'
    }
    return answer == correct_answers.get(question, "")

def submit_answer_3(request, lesson, question):
    if request.method == "POST":
        answer = request.POST.get('answer')

        student = request.user.student_profile

        if check_answer_3(question, answer):
            print(student.answers)
            if f"{lesson}" not in student.answers:
                student.answers[f"{lesson}"] = {}
            if f"{question}" not in student.answers[f"{lesson}"]:
                print(student.answers)
                d = {f"{question}" : answer}
                student.answers[f"{lesson}"].update(d)
                print(student.answers)
                student.save()
            context = {
                "answers": student.answers
            }
            return render(request, 'lesson3.html', context)
        else:
            return HttpResponse("invalid", status = 304)
        
def check_answer_3(question, answer):
    print(question)
    print(answer)
    correct_answers = {
        1: 'document.getElementById("phrase").innerHTML = "Hey Everyone"',
        2: 'document.getElementById("tree").style.display = none'
    }
    return answer == correct_answers.get(question, "")

def students_list(request):
    # Ensure profile exists
    student_profile = request.user.student_profile
    friends = [
        {'username': friend.user.username, 'id': friend.user.id}
        for friend in student_profile.friends.all()
    ]
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user)
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user)

    incoming_requests = []
    outgoing_requests = []
    regular_students = []

    # Categorize users
    students = User.objects.exclude(id=request.user.id)  # All users except the current user
    for student in students:

        if student_profile.friends.all().filter(user=student).exists():
            continue
        elif friend_requests_received.filter(from_user=student).exists():
            # Add to incoming friend requests
            friend_request = friend_requests_received.get(from_user=student)
            incoming_requests.append({
                'username': student.username,
                'id': student.id,
                'status': 'Incoming Request',
                'friend_request_id': friend_request.id
            })
        elif friend_requests_sent.filter(to_user=student).exists():
            # Add to outgoing friend requests
            friend_request = friend_requests_sent.get(to_user=student)
            outgoing_requests.append({
                'username': student.username,
                'id': student.id,
                'status': 'Request Sent',
                'friend_request_id': friend_request.id
            })
        else:
            # Add to regular students
            regular_students.append({
                'username': student.username,
                'id': student.id,
                'status': 'Add Friend'
            })

    context = {
        'friends': friends,  # Pass the `friends` queryset directly
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'regular_students': regular_students,
    }
    return render(request, 'student-list.html', context)

def send_friend_request(request, id):
    to_user = User.objects.get(id=id)
    print(to_user)
    created = FriendRequest.objects.create(
        from_user=request.user,
        to_user=to_user
    )
    if created:
        # Friend request successfully created
        pass
    else:
        # Friend request already exists
        pass
    return redirect('students')

def cancel_friend_request(request, friend_request_id):
    print(FriendRequest.objects.all())
    friend_request = FriendRequest.objects.get(id=friend_request_id, from_user=request.user)
    friend_request.delete()
    return redirect('students')

def accept_friend_request(request, friend_request_id):
    # Get the friend request
    friend_request = FriendRequest.objects.get(id=friend_request_id, to_user=request.user)
    
    # Add each other as friends
    request.user.student_profile.friends.add(friend_request.from_user.student_profile)
    friend_request.from_user.student_profile.friends.add(request.user.student_profile)
    
    # Delete the friend request
    friend_request.delete()
    
    return redirect('students')

def remove_friend(request, user_id):
    # Get the user to be removed
    friend = User.objects.get(id=user_id)
    
    # Remove each other as friends
    request.user.student_profile.friends.remove(friend.student_profile)
    friend.student_profile.friends.remove(request.user.student_profile)
    
    return redirect('students')

def collab(request, box_id):
    user_id = request.user.id
    
    collab_box = get_object_or_404(CollabBox, id=box_id)
    
    if not collab_box.allowed_editors.filter(id=user_id).exists() and collab_box.owner.id != user_id:
        read_only = True
    else:
        read_only = False

    # Pass context to the template
    context = {
        'read_only': read_only,
        'user_id': user_id,
        'collab_box_id': box_id,
        'owner_collab_box_id': collab_box.owner.id,
        'curr_page_username': collab_box.owner
    }

    return render(request, 'collab.html', context)

def ajax_get_friend_list(request):
    user = request.user

    # Get IDs of users with a pending outgoing or incoming request
    outgoing_request_ids = FriendRequest.objects.filter(from_user=user).values_list("to_user_id", flat=True)
    incoming_request_ids = FriendRequest.objects.filter(to_user=user).values_list("from_user_id", flat=True)

    # Friends list
    friends = list(user.student_profile.friends.values("id", "user__username"))

    # Incoming Friend Requests
    incoming_requests = list(FriendRequest.objects.filter(to_user=user).values("id", "from_user__username"))

    # Outgoing Friend Requests
    outgoing_requests = list(FriendRequest.objects.filter(from_user=user).values("id", "to_user__username"))

    # Regular students (not friends, not in pending requests, not the current user)
    regular_students = list(
        User.objects.exclude(id__in=user.student_profile.friends.values_list("user_id", flat=True))
        .exclude(id__in=outgoing_request_ids)
        .exclude(id__in=incoming_request_ids)
        .exclude(id=user.id)
        .values("id", "username")
    )


    return JsonResponse({
        "friends": friends,
        "incoming_requests": incoming_requests,
        "outgoing_requests": outgoing_requests,
        "regular_students": regular_students,
    })


def ajax_accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
    request.user.student_profile.friends.add(friend_request.from_user.student_profile)
    friend_request.from_user.student_profile.friends.add(request.user.student_profile)
    friend_request.delete()
    return JsonResponse({
        "success": True,
        "friend": {
            "id": friend_request.from_user.id,
            "user__username": friend_request.from_user.username
        }
    })

def ajax_cancel_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id, from_user=request.user)
    incoming_request_id = friend_request.id
    friend_request.delete()
    return JsonResponse({
        "success": True,
        "incoming_request_id": incoming_request_id,
    })

def ajax_send_friend_request(request, student_id):
    to_user = User.objects.get(id=student_id)
    new_item = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    new_item.save()
    return JsonResponse({
        "success": True,
        "outgoing_request": {"id": new_item.id, "to_user__username": to_user.username},
    })

def ajax_remove_friend(request, student_id):
    # Get the user to be removed
    current_user_profile = request.user.student_profile
    friend = request.user.student_profile.friends.get(id=student_id)

    # Remove the friendship
    current_user_profile.friends.remove(friend)
    friend.friends.remove(current_user_profile)

    # Return updated friend list
    return ajax_get_friend_list(request)

def students_list(request):
    # Add your logic to fetch and display students here
    return render(request, "student-list.html")
