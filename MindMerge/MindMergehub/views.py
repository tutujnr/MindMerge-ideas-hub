from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Message, Profile
from .forms import RoomForm, UserUpdateForm, ProfileUpdateForm, CustomUserCreationForm
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
import random


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("register")
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    context = {'page': page}
    return render(request, "base/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect("login")

def registerPage(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()

            if User.objects.filter(username=user.username).exists():
                messages.error(request, "Account already exists, try logging in")
                return redirect("login")
            else:
                verification_code = str(random.randint(100000, 999999))
                send_mail(
                    'Email Verification Code',
                    f'Your verification code is {verification_code}',
                    'evanslangat417@gmail.com',
                    [form.cleaned_data.get('email')],
                    fail_silently=False,
                )

                request.session['verification_code'] = verification_code
                request.session['user_data'] = {
                    'username': user.username,
                    'email': user.email,
                    'password1': form.cleaned_data.get('password1'),
                    'password2': form.cleaned_data.get('password2'),
                }
                messages.success(request, "Verification successful")
                return redirect("verify_email")
        else:
            messages.error(request, "An error occurred during registration")

    context = {'form': form, 'page': page}
    return render(request, "base/login_register.html", context)

def verifyEmail(request):
    if request.method == "POST":
        verification_code = request.POST.get('email_verification_code')
        if verification_code == request.session.get('verification_code'):
            user_data = request.session.get('user_data')
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password1']
            )
            messages.success(request, "Account was created successfully")
            return redirect("login")
        else:
            messages.error(request, "Invalid verification code")

    return render(request, "base/verify_email.html")

def base(request):
    return render(request, 'base/base.html')

def about(request):
    return render(request, 'base/about.html')

def contacts(request):
    return render(request, 'base/contacts.html')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(host__username__icontains=q)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()

    comments = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(room__name__icontains=q) |
        Q(body__icontains=q) |
        Q(user__username__icontains=q)
    )[:20]

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'comments': comments,
    }
    return render(request, "base/home.html", context)

def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    topics = Topic.objects.filter(
        name__icontains=q
    ).annotate(
        room_count=Count('room')
    ).order_by('-room_count')
    
    context = {
        'topics': topics,
        'topics_count': topics.count(),
    }
    return render(request, 'base/topics.html', context)

@login_required(login_url='/login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    comments = room.message_set.all().order_by('created')
    participants = room.participants.all()  

    if request.method == "POST":
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        room.save()
        return redirect("room", pk=room.id)
        
    context = {
        'room': room, 
        'comments': comments,
        'participants': participants,
        }
    return render(request, "base/room.html", context)

@login_required(login_url='/login')
def createRoom(request):
    page = 'create-room'
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")
        
    return render(request, "base/room_form.html", context={'form': form, 'page': page})

@login_required(login_url='/login')
def updateRoom(request, pk):
    page = 'update-room'
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed to edit this room")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    return render(request, "base/room_form.html", context={'form': form, 'page': page})

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room")
    
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", context={'room': room})

@login_required(login_url='/login')
def deleteComment(request, pk):
    comment = Message.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse("You are not allowed to delete this comment")
    
    if request.method == "POST":
        room_id = comment.room.id if comment.room else None
        comment.delete()
        if room_id:
            return redirect("room", pk=room_id)
        return redirect("home")
    if request.GET.get('from') == 'home':
        comment.delete()
        return redirect("home")
    return render(request, "base/delete.html", context={'comment': comment})

@login_required(login_url='/login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)

    profile = Profile.objects.get_or_create(user=user)
    rooms = user.room_set.all()
    comments = Message.objects.filter(
            user=user
        ).select_related('user', 'room').order_by('-updated', '-created')[:5]

    topics = Topic.objects.annotate(
            room_count=Count('room', filter=Q(room__host=user))
        ).order_by('-room_count')
    context = {
        'user': user, 
        'rooms': rooms, 
        'comments': comments,
        'topics': topics,
        'profile': profile,
        }
    return render(request, "base/profile.html", context)

@login_required(login_url='/login')
def updateUser(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            if request.POST.get('remove_avatar') == 'true':
                profile.avatar.delete(save=False)  
                profile.avatar = None
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', pk=request.user.id)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'base/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required(login_url='/login')
def deleteProfile(request):
    user = request.user
    if request.method == "POST":
        user.delete()
        return redirect("/login")
    return render(request, "base/delete.html", context={'user': user})