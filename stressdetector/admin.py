from django.contrib import admin
from .models import (
    UserProfile, StressPrediction, MoodJournal, StressComparison,
    DailyStreak, StressTip, BreathingExercise, MotivationalQuote, UserSession
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_state', 'streak_days', 'total_predictions', 'last_activity']
    list_filter = ['avatar_state']
    search_fields = ['user__username']

@admin.register(StressPrediction)
class StressPredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'stress_level', 'mood_tag', 'stress_type', 'confidence', 'created_at']
    list_filter = ['stress_level', 'mood_tag', 'stress_type', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']

@admin.register(MoodJournal)
class MoodJournalAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_title', 'text_sentiment', 'combined_stress_level', 'created_at']
    list_filter = ['text_sentiment', 'combined_stress_level', 'created_at']
    search_fields = ['user__username', 'title', 'text']
    readonly_fields = ['created_at']

@admin.register(StressComparison)
class StressComparisonAdmin(admin.ModelAdmin):
    list_display = ['user', 'before_stress_level', 'after_stress_level', 'improvement_score', 'created_at']
    list_filter = ['before_stress_level', 'after_stress_level', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'improvement_score']

@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'check_in_count', 'last_check_in']
    list_filter = ['date']
    search_fields = ['user__username']

@admin.register(StressTip)
class StressTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'stress_level', 'category', 'is_active']
    list_filter = ['stress_level', 'category', 'is_active']
    search_fields = ['title', 'content']

@admin.register(BreathingExercise)
class BreathingExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'inhale_time', 'hold_time', 'exhale_time', 'cycles', 'get_total_duration']
    list_filter = ['is_active']

@admin.register(MotivationalQuote)
class MotivationalQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_short', 'author', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['quote', 'author']
    
    def quote_short(self, obj):
        return obj.quote[:50] + '...' if len(obj.quote) > 50 else obj.quote

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'duration', 'pages_visited', 'predictions_made']
    list_filter = ['login_time']
    search_fields = ['user__username']
    readonly_fields = ['login_time', 'duration']
