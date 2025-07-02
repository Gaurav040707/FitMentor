from django import forms
from backoffice_engine.models import *
from .models import *

class UserRegistration(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name","email","password"]
class UserUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name"]
class ProfileForm(forms.ModelForm):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("gold", "Gold"),
    ]

    plan = forms.ChoiceField(choices=PLAN_CHOICES, initial="free")

    class Meta:
        model = User
        fields = ["name", "email", "password", "plan"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
}


class UserHealthForm(forms.ModelForm):
    class Meta:
        model = User_health
        fields = ['gender', 'age', 'weight', 'height', 'medical_conditions']
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'height': 'Height (in cm)',
        }


    def save(self, commit=True):
        # First get an unsaved instance
        instance: User_health = super().save(commit=False)

        # Compute BMI (height expected in cm)
        if instance.height and instance.weight:
            h_m = instance.height / 100
            instance.bmi = round(instance.weight / (h_m * h_m), 1)
        else:
            instance.bmi = None

        # Now save
        if commit:
            instance.save()
        return instance
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'placeholder': 'Write your feedback here…',
                'rows': 4,
            })
        }