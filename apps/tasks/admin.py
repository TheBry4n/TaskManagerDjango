from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'due_date', 'reactivation_count', 'created_at', 'is_overdue_display']
    list_filter = ['status', 'due_date', 'created_at', 'reactivation_count', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'reactivation_count']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'due_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'reactivation_count'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_display(self, obj):
        """Display overdue status in admin list"""
        if obj.is_overdue:
            return "🔴 Overdue"
        return "🟢 On Time"
    is_overdue_display.short_description = 'Overdue Status'
    is_overdue_display.boolean = True
