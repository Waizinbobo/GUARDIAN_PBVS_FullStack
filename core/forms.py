from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Appeal, Report, Verification


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, label='Full name')

    class Meta:
        model = User
        fields = ('first_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user


class VerificationForm(forms.ModelForm):
    consent_confirmed = forms.BooleanField(label='I confirm that lawful consent has been obtained.')

    class Meta:
        model = Verification
        fields = ('employee_id', 'nrc_no', 'previous_company', 'consent_confirmed')


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('reporter_name', 'reporter_email', 'report_type', 'subject', 'details', 'attachment')


class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ('risk_record', 'reason', 'supporting_file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['risk_record'].queryset = self.fields['risk_record'].queryset.filter(is_active=True)
