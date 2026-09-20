from django.utils import timezone
from .models import AuditLog, Employee, RiskRecord, Verification, VerificationResult


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')


def audit(request, action, instance=None, detail=None):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=instance.__class__.__name__ if instance else '',
        object_id=str(getattr(instance, 'pk', '')),
        detail=detail or {},
        ip_address=client_ip(request),
    )


def run_verification(verification):
    employee = Employee.objects.filter(employee_id__iexact=verification.employee_id, nrc_no__iexact=verification.nrc_no).first()
    records = RiskRecord.objects.none()
    if employee:
        records = employee.risk_records.filter(is_active=True)
    priority = {'BLACK': 4, 'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    record = max(records, key=lambda row: priority[row.risk_level], default=None)
    risk_level = record.risk_level if record else RiskRecord.RiskLevel.GREEN
    summary = record.reason if record else 'No active adverse risk record matched the submitted identifiers.'
    result, _ = VerificationResult.objects.update_or_create(
        verification=verification,
        defaults={'risk_level': risk_level, 'case_summary': summary, 'matched_employee': employee, 'completed_at': timezone.now()},
    )
    verification.status = Verification.Status.COMPLETE
    verification.save(update_fields=['status', 'updated_at'])
    return result
