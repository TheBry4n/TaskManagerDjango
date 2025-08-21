from django import forms
from .models import Task
from django.utils import timezone

class BaseTaskForm(forms.ModelForm):
    """Base form for common methods"""

    def clean_future_datetime(self, field_name):
        """Common validation for future datetime fields"""
        datetime_value = self.cleaned_data.get(field_name)
        if datetime_value and datetime_value <= timezone.now():
            raise forms.ValidationError(
                f"{field_name.replace('_', ' ').title()} must be in the future"
            )
        return datetime_value


class TaskForm(BaseTaskForm, forms.ModelForm):
    """Form for creating and updating tasks"""
    class Meta:
        model = Task
        fields = ["title", "description", "due_date"]
        widgets = {
            "title" : forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter task title"
            }),
            "description" : forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter task description"
            }),
            "due_date" : forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local",
            })
        }
    
    def clean_due_date(self):
        return self.clean_future_datetime('due_date')
    
    def clean(self):
        """Custom validation for the form"""
        cleaned_data = super().clean()
        
        # For updates, only active tasks can be edited, so always require future dates
        if self.instance and self.instance.pk:
            due_date = cleaned_data.get('due_date')
            if due_date and due_date <= timezone.now():
                raise forms.ValidationError(
                    "Due date must be in the future for active tasks"
                )
        
        return cleaned_data

class TaskReactivationForm(BaseTaskForm, forms.Form):
    """Form for reactivating a failed task"""
    new_due_date = forms.DateTimeField(
        widget = forms.DateTimeInput(attrs = {
            "class" : "form-control",
            "type" : "datetime-local",
        }),
        label = "New Due Date",
    )
    
    def clean_new_due_date(self):
        return self.clean_future_datetime('new_due_date')

