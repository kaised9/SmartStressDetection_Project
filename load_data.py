import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartStressDetection.settings')
django.setup()

from stressdetector.models import StressTip, BreathingExercise, MotivationalQuote

# Create stress tips
StressTip.objects.create(
    title='Deep Breathing',
    content='Take 5 deep breaths, inhaling slowly through your nose and exhaling through your mouth.',
    stress_level='All',
    category='Breathing'
)

StressTip.objects.create(
    title='Take a Walk',
    content='Go for a 10-minute walk outside. Fresh air and light exercise can help reduce stress.',
    stress_level='Medium',
    category='Exercise'
)

StressTip.objects.create(
    title='Meditation',
    content='Practice mindfulness meditation for 10 minutes. Focus on your breath and let thoughts pass without judgment.',
    stress_level='High',
    category='Mindfulness'
)

# Create breathing exercises
BreathingExercise.objects.create(
    name='Box Breathing',
    description='A simple breathing technique that helps calm the nervous system.',
    inhale_time=4,
    hold_time=4,
    exhale_time=4,
    cycles=5
)

BreathingExercise.objects.create(
    name='4-7-8 Breathing',
    description='A breathing pattern that promotes relaxation and sleep.',
    inhale_time=4,
    hold_time=7,
    exhale_time=8,
    cycles=4
)

# Create motivational quotes
MotivationalQuote.objects.create(
    quote='You are stronger than you think.',
    author='Unknown',
    category='Strength'
)

MotivationalQuote.objects.create(
    quote='Every day is a new beginning.',
    author='Unknown',
    category='New Beginnings'
)

MotivationalQuote.objects.create(
    quote='Progress, not perfection.',
    author='Unknown',
    category='Progress'
)

print('Initial data created successfully!')