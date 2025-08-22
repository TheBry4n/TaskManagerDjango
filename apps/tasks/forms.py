from django import forms
from .models import Task
from .utils import validate_future_datetime


class TaskForm(forms.ModelForm):
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
        return validate_future_datetime(self.cleaned_data.get('due_date'), 'due_date')
    
    def clean(self):
        """Custom validation for the form"""
        cleaned_data = super().clean()
        
        # For updates, only active tasks can be edited, so always require future dates
        if self.instance and self.instance.pk:
            due_date = cleaned_data.get('due_date')
            if due_date:
                validate_future_datetime(due_date, 'due_date')
        
        return cleaned_data

class TaskReactivationForm(forms.Form):
    """Form for reactivating a failed task"""
    new_due_date = forms.DateTimeField(
        widget = forms.DateTimeInput(attrs = {
            "class" : "form-control",
            "type" : "datetime-local",
        }),
        label = "New Due Date",
    )
    
    def clean_new_due_date(self):
        """Validate that the new due date is in the future"""
        return validate_future_datetime(self.cleaned_data.get('new_due_date'), 'new_due_date')

