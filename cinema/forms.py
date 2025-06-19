from django import forms
from django.contrib.auth.models import User
from .models import Profile

class EditProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank to keep current password.")

    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone_number', 'bio']

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        password = self.cleaned_data.get('password', '')

        if password:
            user.set_password(password)

        if commit:
            user.save()
            profile.save()
        return profile
