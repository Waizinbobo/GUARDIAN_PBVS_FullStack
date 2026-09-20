import uuid
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(TimeStampedModel):
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        VERIFIED = 'VERIFIED', 'Verified'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    name = models.CharField(max_length=200, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='companies')

    def __str__(self):
        return self.name


class Employee(TimeStampedModel):
    employee_id = models.CharField(max_length=80, unique=True)
    nrc_no = models.CharField(max_length=80, unique=True)
    full_name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='employees/', blank=True)
    previous_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='former_employees')

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


class Case(TimeStampedModel):
    class CaseStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        REVIEW = 'REVIEW', 'Under Review'
        CLOSED = 'CLOSED', 'Closed'

    reference = models.CharField(max_length=40, unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    case_type = models.CharField(max_length=120)
    summary = models.TextField()
    status = models.CharField(max_length=20, choices=CaseStatus.choices, default=CaseStatus.OPEN)
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='cases')
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='cases')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class RiskRecord(TimeStampedModel):
    class RiskLevel(models.TextChoices):
        BLACK = 'BLACK', 'Critical Risk'
        RED = 'RED', 'High Risk'
        YELLOW = 'YELLOW', 'Warning'
        GREEN = 'GREEN', 'Verified'

    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    reason = models.TextField()
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.CASCADE, related_name='risk_records')
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='risk_records')
    case = models.ForeignKey(Case, null=True, blank=True, on_delete=models.SET_NULL, related_name='risk_records')
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        subject = self.employee or self.company
        return f"{subject}: {self.get_risk_level_display()}"


class Verification(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETE = 'COMPLETE', 'Complete'
        REJECTED = 'REJECTED', 'Rejected'

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    employee_id = models.CharField(max_length=80)
    nrc_no = models.CharField(max_length=80)
    previous_company = models.CharField(max_length=200, blank=True)
    consent_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return str(self.reference)


class VerificationResult(TimeStampedModel):
    verification = models.OneToOneField(Verification, on_delete=models.CASCADE, related_name='result')
    risk_level = models.CharField(max_length=10, choices=RiskRecord.RiskLevel.choices)
    case_summary = models.TextField(blank=True)
    matched_employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_results')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Result {self.verification.reference}"


class Evidence(TimeStampedModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='evidence/%Y/%m/', validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])])
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class News(TimeStampedModel):
    class Category(models.TextChoices):
        NEWS = 'NEWS', 'News'
        WARNING = 'WARNING', 'Warning'
        NOTICE = 'NOTICE', 'Public Notice'
        UPDATE = 'UPDATE', 'Update'

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Report(TimeStampedModel):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        REVIEW = 'REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    reporter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reporter_name = models.CharField(max_length=150)
    reporter_email = models.EmailField()
    report_type = models.CharField(max_length=100)
    subject = models.CharField(max_length=250)
    details = models.TextField()
    attachment = models.FileField(upload_to='reports/%Y/%m/', blank=True, validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    def __str__(self):
        return self.subject


class Appeal(TimeStampedModel):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        REVIEW = 'REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        DENIED = 'DENIED', 'Denied'

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    appellant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appeals')
    risk_record = models.ForeignKey(RiskRecord, on_delete=models.CASCADE, related_name='appeals')
    reason = models.TextField()
    supporting_file = models.FileField(upload_to='appeals/%Y/%m/', blank=True, validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    decision_notes = models.TextField(blank=True)

    def __str__(self):
        return str(self.reference)


class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} {self.model_name}"

# Create your models here.
