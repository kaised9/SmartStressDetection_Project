from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from datetime import timedelta
import json
import random
from .models import StressPrediction, UserProfile, StressTip, BreathingExercise, MotivationalQuote, MoodJournal, StressComparison

@login_required(login_url='login')
def home(request):
    # Get user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check for sleep mode (no activity for 3 days)
    days_inactive = (timezone.now() - profile.last_activity).days
    if days_inactive >= 3:
        profile.avatar_state = 'sleeping'
        profile.save()
    
    # Get weekly stress data
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Get latest prediction for avatar
    latest_prediction = StressPrediction.objects.filter(user=request.user).order_by('-created_at').first()
    
    # Update avatar state based on latest prediction
    if latest_prediction and days_inactive < 3:
        if latest_prediction.stress_level == 'Low':
            profile.avatar_state = 'happy'
        elif latest_prediction.stress_level == 'Medium':
            profile.avatar_state = 'neutral'
        else:
            profile.avatar_state = 'stressed'
        profile.save()
    
    # Get random tips and quotes
    tips = list(StressTip.objects.filter(is_active=True))
    exercises = list(BreathingExercise.objects.filter(is_active=True))
    quotes = list(MotivationalQuote.objects.filter(is_active=True))
    
    selected_tips = random.sample(tips, min(3, len(tips))) if tips else []
    selected_exercise = random.choice(exercises) if exercises else None
    selected_quote = random.choice(quotes) if quotes else None
    
    context = {
        'profile': profile,
        'latest_prediction': latest_prediction,
        'days_inactive': days_inactive,
        'tips': selected_tips,
        'exercise': selected_exercise,
        'quote': selected_quote,
        'labels': json.dumps(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
        'data': json.dumps([60, 70, 65, 80, 75, 60, 55])
    }
    
    return render(request, 'stressdetector/home.html', context)

def predict(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login to analyze your stress level.")
        return redirect('login')
    
    if request.method == 'POST' and request.FILES.get('face_image'):
        image = request.FILES['face_image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        
        try:
            # Mock prediction - replace with actual ML model
            prediction_data = {
                'stress_level': 'Medium',
                'mood_tag': 'Neutral',
                'stress_type': 'Work',
                'confidence': 78
            }
            
            # Save to database
            prediction = StressPrediction.objects.create(
                user=request.user,
                image=image,
                stress_level=prediction_data['stress_level'],
                mood_tag=prediction_data['mood_tag'],
                stress_type=prediction_data['stress_type'],
                confidence=prediction_data['confidence']
            )
            
            messages.success(request, "Stress analysis completed successfully!")
        except Exception as e:
            messages.error(request, f"Error processing image: {str(e)}")
    
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created successfully for {username}! Please log in.")
            return redirect('login')
        else:
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
def history(request):
    predictions = StressPrediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'stressdetector/history.html', {'predictions': predictions})

@login_required(login_url='login')
def journal(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        image = request.FILES.get('image')
        
        # Simple sentiment analysis (mock)
        text_lower = text.lower()
        if any(word in text_lower for word in ['happy', 'good', 'great', 'excellent']):
            text_sentiment = 'Positive'
        elif any(word in text_lower for word in ['sad', 'bad', 'terrible', 'awful']):
            text_sentiment = 'Negative'
        else:
            text_sentiment = 'Neutral'
        
        # Create journal entry
        journal = MoodJournal.objects.create(
            user=request.user,
            text=text,
            image=image if image else None,
            text_sentiment=text_sentiment,
            combined_stress_level='Medium'  # Default for now
        )
        
        messages.success(request, 'Journal entry saved successfully!')
        return redirect('journal')
    
    # Get journal entries
    entries = MoodJournal.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'stressdetector/journal.html', {'entries': entries})

@login_required(login_url='login')
def compare(request):
    if request.method == 'POST':
        before_image = request.FILES.get('before_image')
        after_image = request.FILES.get('after_image')
        
        if before_image and after_image:
            fs = FileSystemStorage()
            
            # Process before image
            before_filename = fs.save(before_image.name, before_image)
            
            # Process after image
            after_filename = fs.save(after_image.name, after_image)
            
            try:
                # Mock predictions
                before_stress = 'High'
                after_stress = 'Medium'
                
                # Determine improvement
                improvement = after_stress != before_stress
                
                # Save comparison
                comparison = StressComparison.objects.create(
                    user=request.user,
                    before_image=before_image,
                    after_image=after_image,
                    before_stress_level=before_stress,
                    after_stress_level=after_stress,
                    before_confidence=75,
                    after_confidence=70,
                    improvement_score=25  # Mock improvement score
                )
                
                messages.success(request, 'Images compared successfully!')
                return render(request, 'stressdetector/comparison_result.html', {
                    'comparison': comparison,
                    'improvement': improvement
                })
                
            except Exception as e:
                messages.error(request, f'Error processing images: {str(e)}')
                return redirect('compare')
    
    return render(request, 'stressdetector/compare.html')

@login_required(login_url='login')
def trends_api(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    data = StressPrediction.objects.filter(
        user=request.user,
        created_at__date__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(created_at)'}
    ).values('day', 'stress_level').annotate(count=models.Count('id'))
    
    dates = []
    stress_counts = {'Low': [], 'Medium': [], 'High': []}
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        day_data = [d for d in data if d['day'] == current_date]
        
        for level in ['Low', 'Medium', 'High']:
            count = next((d['count'] for d in day_data if d['stress_level'] == level), 0)
            stress_counts[level].append(count)
    
    return JsonResponse({
        'dates': dates,
        'stress_counts': stress_counts
    })