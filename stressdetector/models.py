from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def get_image_upload_path(instance, filename):
    """Generate upload path for user images"""
    return os.path.join('user_images', f'user_{instance.user.id}', filename)

def get_journal_image_path(instance, filename):
    """Generate upload path for journal images"""
    return os.path.join('journal_images', f'user_{instance.user.id}', filename)

def get_comparison_image_path(instance, filename):
    """Generate upload path for comparison images"""
    return os.path.join('comparison_images', f'user_{instance.user.id}', filename)

class UserProfile(models.Model):
    """Extended user profile with stress tracking information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_state = models.CharField(
        max_length=20, 
        choices=[
            ('happy', 'Happy 😄'),
            ('neutral', 'Neutral 😐'),
            ('stressed', 'Stressed 😣'),
            ('sleeping', 'Sleeping 😴')
        ],
        default='neutral'
    )
    last_activity = models.DateTimeField(auto_now=True)
    streak_days = models.IntegerField(default=0)
    total_predictions = models.IntegerField(default=0)
    total_journal_entries = models.IntegerField(default=0)
    total_comparisons = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_avatar_state(self, stress_level):
        """Update avatar based on stress level"""
        if stress_level == 'Low':
            self.avatar_state = 'happy'
        elif stress_level == 'Medium':
            self.avatar_state = 'neutral'
        else:
            self.avatar_state = 'stressed'
        self.save()

class StressPrediction(models.Model):
    """Model for storing stress prediction results"""
    STRESS_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ]
    
    MOOD_TAGS = [
        ('Happy', 'Happy'),
        ('Neutral', 'Neutral'),
        ('Sad', 'Sad')
    ]
    
    STRESS_TYPES = [
        ('Work', 'Work'),
        ('Personal', 'Personal'),
        ('Social', 'Social'),
        ('Health', 'Health'),
        ('Financial', 'Financial'),
        ('Other', 'Other')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_upload_path)
    stress_level = models.CharField(max_length=10, choices=STRESS_LEVELS)
    mood_tag = models.CharField(max_length=10, choices=MOOD_TAGS)
    stress_type = models.CharField(max_length=20, choices=STRESS_TYPES, default='Other')
    confidence = models.IntegerField(help_text="Confidence percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stress Prediction"
        verbose_name_plural = "Stress Predictions"
    
    def __str__(self):
        return f"{self.user.username} - {self.stress_level} stress on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Update user profile when saving a prediction
        super().save(*args, **kwargs)
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.total_predictions += 1
        profile.last_activity = timezone.now()
        profile.update_avatar_state(self.stress_level)
        profile.save()

class MoodJournal(models.Model):
    """Model for mood journal entries with text and image fusion"""
    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Neutral', 'Neutral'),
        ('Negative', 'Negative')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    image = models.ImageField(upload_to=get_journal_image_path, blank=True, null=True)
    text_sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    image_stress_level = models.CharField(
        max_length=10, 
        choices=StressPrediction.STRESS_LEVELS, 
        blank=True, 
        null=True
    )
    combined_stress_level = models.CharField(max_length=10, choices=StressPrediction.STRESS_LEVELS)
    stress_keywords = models.JSONField(default=list, blank=True, help_text="List of stress-related keywords found in text")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mood Journal"
        verbose_name_plural = "Mood Journals"
    
    def __str__(self):
        return f"{self.user.username}'s Journal - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_title(self):
        """Generate title if not provided"""
        if self.title:
            return self.title
        
        # Use first few words of text as title
        words = self.text.split()[:5]
        return ' '.join(words) + ('...' if len(self.text.split()) > 5 else '')
    
    def save(self, *args, **kwargs):
        # Update user profile when saving a journal entry
        super().save(*args, **kwargs)
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.total_journal_entries += 1
        profile.last_activity = timezone.now()
        profile.update_avatar_state(self.combined_stress_level)
        profile.save()

class StressComparison(models.Model):
    """Model for before/after stress comparison"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    before_image = models.ImageField(upload_to=get_comparison_image_path)
    after_image = models.ImageField(upload_to=get_comparison_image_path)
    before_stress_level = models.CharField(max_length=10, choices=StressPrediction.STRESS_LEVELS)
    after_stress_level = models.CharField(max_length=10, choices=StressPrediction.STRESS_LEVELS)
    before_confidence = models.IntegerField()
    after_confidence = models.IntegerField()
    improvement_score = models.IntegerField(help_text="Percentage improvement (can be negative)")
    comparison_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stress Comparison"
        verbose_name_plural = "Stress Comparisons"
    
    def __str__(self):
        return f"{self.user.username}'s Comparison - {self.created_at.strftime('%Y-%m-%d')}"
    
    def calculate_improvement(self):
        """Calculate improvement score based on stress levels"""
        stress_values = {'Low': 1, 'Medium': 2, 'High': 3}
        before_value = stress_values[self.before_stress_level]
        after_value = stress_values[self.after_stress_level]
        
        # Calculate percentage improvement
        if before_value == after_value:
            self.improvement_score = 0
        elif after_value < before_value:
            # Stress decreased
            self.improvement_score = ((before_value - after_value) / before_value) * 100
        else:
            # Stress increased
            self.improvement_score = -((after_value - before_value) / after_value) * 100
        
        self.save()
    
    def save(self, *args, **kwargs):
        # Update user profile when saving a comparison
        super().save(*args, **kwargs)
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.total_comparisons += 1
        profile.last_activity = timezone.now()
        profile.save()

class DailyStreak(models.Model):
    """Model for tracking user's daily check-in streaks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_count = models.IntegerField(default=0)
    last_check_in = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
        verbose_name = "Daily Streak"
        verbose_name_plural = "Daily Streaks"
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class StressTip(models.Model):
    """Model for storing stress management tips"""
    STRESS_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('All', 'All')
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    stress_level = models.CharField(max_length=10, choices=STRESS_LEVELS, default='All')
    category = models.CharField(max_length=50, default='General')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['stress_level', 'category']
        verbose_name = "Stress Tip"
        verbose_name_plural = "Stress Tips"
    
    def __str__(self):
        return f"{self.title} - {self.stress_level} stress"

class BreathingExercise(models.Model):
    """Model for breathing exercises"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    inhale_time = models.IntegerField(help_text="Inhale duration in seconds")
    hold_time = models.IntegerField(help_text="Hold breath duration in seconds")
    exhale_time = models.IntegerField(help_text="Exhale duration in seconds")
    cycles = models.IntegerField(default=5, help_text="Number of breathing cycles")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Breathing Exercise"
        verbose_name_plural = "Breathing Exercises"
    
    def __str__(self):
        return self.name
    
    def get_total_duration(self):
        """Calculate total duration of the exercise"""
        cycle_duration = self.inhale_time + self.hold_time + self.exhale_time
        return cycle_duration * self.cycles

class MotivationalQuote(models.Model):
    """Model for motivational quotes"""
    quote = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, default='General')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Motivational Quote"
        verbose_name_plural = "Motivational Quotes"
    
    def __str__(self):
        return f"{self.quote[:50]}... - {self.author}"

class UserSession(models.Model):
    """Model for tracking user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    pages_visited = models.IntegerField(default=0)
    predictions_made = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    
    def calculate_duration(self):
        """Calculate session duration"""
        if self.logout_time:
            self.duration = self.logout_time - self.login_time
            self.save()