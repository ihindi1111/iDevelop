from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from idevelop.models import Profile, Student

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 2}),
            'profile_picture': forms.ClearableFileInput(),
        }
