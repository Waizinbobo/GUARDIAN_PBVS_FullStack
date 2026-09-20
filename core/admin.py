from django.contrib import admin
from .models import Appeal, AuditLog, Case, Company, Employee, Evidence, News, Report, RiskRecord, Verification, VerificationResult


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'verification_status', 'updated_at')
    list_filter = ('verification_status',)
    search_fields = ('name', 'registration_number')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'nrc_no', 'previous_company')
    search_fields = ('employee_id', 'full_name', 'nrc_no')


@admin.register(RiskRecord)
class RiskRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'company', 'risk_level', 'is_active', 'is_public', 'updated_at')
    list_filter = ('risk_level', 'is_active', 'is_public')


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'requested_by', 'employee_id', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('employee_id', 'nrc_no')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('subject', 'reporter_email', 'report_type', 'status', 'created_at')
    list_filter = ('status', 'report_type')


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('reference', 'appellant', 'risk_record', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published', 'published_at')
    list_filter = ('category', 'published')

admin.site.register(Case)
admin.site.register(Evidence)
admin.site.register(VerificationResult)
admin.site.register(AuditLog)

admin.site.site_header = 'GUARDIAN (PBVS) Administration'
admin.site.site_title = 'GUARDIAN Admin'

# Register your models here.
