from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
import os
from .models import StressPrediction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created successfully for {username}! Please log in.")
            return redirect('login')
        else:
            # Display form errors if validation fails
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    return render(request, 'stressdetector/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
def home(request):
    # Dummy data for weekly stress trends
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [60, 70, 65, 80, 75, 60, 55]
    return render(request, 'stressdetector/home.html', {
        'labels': labels,
        'data': data,
    })

def predict(request):
    prediction = None
    if request.method == 'POST' and request.FILES.get('face_image'):
        image = request.FILES['face_image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_path = fs.path(filename)
        # Mock prediction
        prediction = {
            'stress_level': 'Medium',
            'mood': 'Neutral',
            'stress_type': 'Work',
            'confidence': 78,
        }
        # Save to database if user is authenticated
        if request.user.is_authenticated:
            StressPrediction.objects.create(
                user=request.user,
                image=image,
                stress_level=prediction['stress_level'],
                mood=prediction['mood'],
                stress_type=prediction['stress_type'],
                confidence=prediction['confidence']
            )
        os.remove(image_path)
    # Dummy data for weekly stress trends
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [60, 70, 65, 80, 75, 60, 55]
    return render(request, 'stressdetector/home.html', {
        'prediction': prediction,
        'labels': labels,
        'data': data,
    })

def trends_api(request):
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [60, 70, 65, 80, 75, 60, 55]
    return JsonResponse({'labels': labels, 'data': data})

@login_required(login_url='login')
def history(request):
    predictions = StressPrediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'stressdetector/history.html', {'predictions': predictions})