from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Create Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Create Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Confirm Password'
        })
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input ms-1'})
    )
    height = forms.FloatField(
        label="Height ()",
        widget=forms.NumberInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Your Height (in cm)'
        })
    )
    weight = forms.FloatField(
        label="Weight (kg)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Your Weight (in kg)'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'gender', 'height', 'weight']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hash password

        # Convert height from cm to meters and calculate BMI
        user.height = self.cleaned_data["height"] / 100
        user.weight = self.cleaned_data["weight"]

        if user.height > 0:
            user.bmi = round(user.weight / (user.height ** 2), 2)

        if commit:
            user.save()
        return user

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'height', 'weight']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['height'].label = 'Height (m)'
        self.fields['weight'].label = 'Weight (kg)'