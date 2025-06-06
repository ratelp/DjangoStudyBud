
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "User or Password does not exist")

    context = {'page' : 'login'}
    return render(request, 'base/login_register.html', context)

def registerUser(request):
    form = UserCreationForm()
    context = {'form': form} 

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")

    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    
    q = request.GET.get('q','')

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
        )

    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    messagesRoom = Message.objects.filter(
        Q(room__topic__name__icontains=q)
        )

    context = {'rooms': rooms, 'topics' : topics, 'room_count': room_count, 'messagesRoom' : messagesRoom}
    return render(request,'base/home.html', context)


def room(request,pk):
    room = Room.objects.get(id=pk)
    messagesRoom = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)


    context = {'room' : room, 'messagesRoom' : messagesRoom, 'participants' : participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    messagesRoom = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'rooms' : rooms, 'messagesRoom' : messagesRoom, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host = request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect('home')


    context = {'form' : form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form' : form, 'topics' : topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj' : room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    context = {'obj' : message}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request,'base/update-user.html', {'form' : form})

def topicsPage(request):


    q = request.GET.get('q','')

    topics = Topic.objects.filter(
        Q(name__icontains=q)
    )
    context = {'topics' : topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):

    messageRooms = Message.objects.all()

    context = {'messageRooms': messageRooms}
    return render(request, 'base/activity.html', context)