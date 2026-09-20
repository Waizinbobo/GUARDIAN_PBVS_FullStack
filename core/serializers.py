from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Appeal, AuditLog, Case, Company, Employee, Evidence, News, Report, RiskRecord, Verification, VerificationResult


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'email')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = '__all__'


class RiskRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = RiskRecord
        fields = '__all__'


class VerificationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationResult
        fields = '__all__'


class VerificationSerializer(serializers.ModelSerializer):
    result = VerificationResultSerializer(read_only=True)

    class Meta:
        model = Verification
        fields = '__all__'
        read_only_fields = ('requested_by', 'status')

    def create(self, validated_data):
        return Verification.objects.create(requested_by=self.context['request'].user, **validated_data)


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('reporter', 'status')


class AppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = '__all__'
        read_only_fields = ('appellant', 'status', 'decision_notes')


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
