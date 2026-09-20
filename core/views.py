from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import AppealForm, RegisterForm, ReportForm, VerificationForm
from .models import Appeal, AuditLog, Case, Company, Employee, Evidence, News, Report, RiskRecord, Verification, VerificationResult
from .permissions import IsOwnerOrStaff, IsStaffOrReadOnly
from .serializers import AppealSerializer, AuditLogSerializer, CaseSerializer, CompanySerializer, EmployeeSerializer, EvidenceSerializer, NewsSerializer, ReportSerializer, RiskRecordSerializer, VerificationSerializer
from .services import audit, run_verification


def home(request):
    return render(request, 'core/index.html')


def about(request):
    return render(request, 'core/about_us.html')


def companies(request):
    companies_qs = Company.objects.all().order_by('name')
    query = request.GET.get('q', '').strip()
    if query:
        companies_qs = companies_qs.filter(Q(name__icontains=query) | Q(registration_number__icontains=query))
    return render(request, 'core/company.html', {'companies': companies_qs, 'query': query})


def blacklist(request):
    records = RiskRecord.objects.filter(is_active=True, is_public=True).select_related('employee', 'company', 'case').order_by('-updated_at')
    level = request.GET.get('risk_level', '').upper()
    query = request.GET.get('q', '').strip()
    if level in RiskRecord.RiskLevel.values:
        records = records.filter(risk_level=level)
    if query:
        records = records.filter(Q(employee__full_name__icontains=query) | Q(company__name__icontains=query) | Q(reason__icontains=query))
    return render(request, 'core/black_list.html', {'risk_records': records, 'query': query, 'selected_level': level})


def news(request):
    articles = News.objects.filter(published=True).order_by('-published_at', '-created_at')
    return render(request, 'core/warining_new.html', {'news_items': articles})


def contact(request):
    form = ReportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user if request.user.is_authenticated else None
        report.save()
        audit(request, 'CREATE', report)
        messages.success(request, f'Report submitted. Reference: {report.reference}')
        return redirect('contact')
    return render(request, 'core/contact.html', {'report_form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        audit(request, 'REGISTER', user)
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    context = {
        'verifications': Verification.objects.filter(requested_by=request.user).order_by('-created_at')[:10],
        'appeals': Appeal.objects.filter(appellant=request.user).order_by('-created_at')[:10],
    }
    if request.user.is_staff:
        context['counts'] = {
            'users': User.objects.count(), 'companies': Company.objects.count(),
            'verifications': Verification.objects.count(), 'reports': Report.objects.count(),
        }
    return render(request, 'core/dashboard.html', context)


@login_required
def verification(request):
    form = VerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        verification_obj = form.save(commit=False)
        verification_obj.requested_by = request.user
        verification_obj.save()
        result = run_verification(verification_obj)
        audit(request, 'VERIFY', verification_obj, {'risk_level': result.risk_level})
        return redirect('verification_result', reference=verification_obj.reference)
    return render(request, 'core/background_verification.html', {'verification_form': form})


@login_required
def verification_result(request, reference):
    verification_obj = get_object_or_404(Verification.objects.select_related('result'), reference=reference)
    if not request.user.is_staff and verification_obj.requested_by != request.user:
        messages.error(request, 'You do not have permission to view this verification.')
        return redirect('dashboard')
    return render(request, 'core/verification_result_dynamic.html', {'verification': verification_obj, 'result': verification_obj.result})


@login_required
def appeal(request):
    form = AppealForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        appeal_obj = form.save(commit=False)
        appeal_obj.appellant = request.user
        appeal_obj.save()
        audit(request, 'CREATE', appeal_obj)
        messages.success(request, f'Appeal submitted. Reference: {appeal_obj.reference}')
        return redirect('dashboard')
    return render(request, 'core/appeal.html', {'form': form})


class StaffWriteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]


class CompanyViewSet(StaffWriteViewSet):
    queryset = Company.objects.all().order_by('name')
    serializer_class = CompanySerializer
    search_fields = ('name', 'registration_number')


class EmployeeViewSet(StaffWriteViewSet):
    queryset = Employee.objects.all().order_by('full_name')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAdminUser]


class CaseViewSet(StaffWriteViewSet):
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.all().order_by('-created_at') if self.request.user.is_staff else Case.objects.filter(is_public=True).order_by('-created_at')


class EvidenceViewSet(StaffWriteViewSet):
    serializer_class = EvidenceSerializer

    def get_queryset(self):
        return Evidence.objects.all().order_by('-created_at') if self.request.user.is_staff else Evidence.objects.filter(is_public=True).order_by('-created_at')


class RiskRecordViewSet(StaffWriteViewSet):
    serializer_class = RiskRecordSerializer

    def get_queryset(self):
        queryset = RiskRecord.objects.select_related('employee', 'company', 'case').filter(is_active=True).order_by('-updated_at')
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        level = self.request.query_params.get('risk_level')
        return queryset.filter(risk_level=level.upper()) if level and level.upper() in RiskRecord.RiskLevel.values else queryset


class NewsViewSet(StaffWriteViewSet):
    serializer_class = NewsSerializer

    def get_queryset(self):
        return News.objects.all() if self.request.user.is_staff else News.objects.filter(published=True)


class VerificationViewSet(viewsets.ModelViewSet):
    serializer_class = VerificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        queryset = Verification.objects.select_related('result').order_by('-created_at')
        return queryset if self.request.user.is_staff else queryset.filter(requested_by=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        run_verification(instance)
        audit(self.request, 'VERIFY', instance)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        queryset = Report.objects.order_by('-created_at')
        return queryset if self.request.user.is_staff else queryset.filter(reporter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class AppealViewSet(viewsets.ModelViewSet):
    serializer_class = AppealSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        queryset = Appeal.objects.order_by('-created_at')
        return queryset if self.request.user.is_staff else queryset.filter(appellant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(appellant=self.request.user)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

# Create your views here.
