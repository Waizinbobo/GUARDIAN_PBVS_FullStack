from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import AuditLog, Company, Employee, RiskRecord, Verification


class GuardianWebTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('hruser', 'hr@example.com', 'StrongPass123!')
        self.company = Company.objects.create(name='Example Co', registration_number='REG-001', verification_status='VERIFIED')
        self.employee = Employee.objects.create(employee_id='EMP-001', nrc_no='12/ABC(N)123456', full_name='Test Person', previous_company=self.company)
        self.record = RiskRecord.objects.create(employee=self.employee, risk_level='RED', reason='Confirmed high-risk test record', is_public=True)

    def test_public_pages_load(self):
        for name in ('home', 'blacklist', 'companies', 'news', 'about', 'contact'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_verification_requires_login(self):
        response = self.client.get(reverse('verification'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_register_login_and_logout(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'New User', 'email': 'new@example.com', 'username': 'newuser',
            'password1': 'AnotherStrong123!', 'password2': 'AnotherStrong123!'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_matching_verification_returns_high_risk(self):
        self.client.login(username='hruser', password='StrongPass123!')
        response = self.client.post(reverse('verification'), {
            'employee_id': 'EMP-001', 'nrc_no': '12/ABC(N)123456',
            'previous_company': 'Example Co', 'consent_confirmed': 'on'
        })
        item = Verification.objects.get(requested_by=self.user)
        self.assertRedirects(response, reverse('verification_result', args=[item.reference]))
        self.assertEqual(item.result.risk_level, 'RED')
        self.assertTrue(AuditLog.objects.filter(action='VERIFY').exists())

    def test_verification_requires_consent(self):
        self.client.login(username='hruser', password='StrongPass123!')
        response = self.client.post(reverse('verification'), {'employee_id': 'EMP-X', 'nrc_no': 'NRC-X'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Verification.objects.count(), 0)

    def test_user_cannot_view_another_users_result(self):
        other = User.objects.create_user('other', password='StrongPass123!')
        item = Verification.objects.create(requested_by=other, employee_id='X', nrc_no='Y', consent_confirmed=True)
        self.client.login(username='hruser', password='StrongPass123!')
        response = self.client.get(reverse('verification_result', args=[item.reference]))
        self.assertRedirects(response, reverse('dashboard'))


class GuardianApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user('apiuser', password='StrongPass123!')
        company = Company.objects.create(name='API Company', registration_number='API-1')
        employee = Employee.objects.create(employee_id='API-E', nrc_no='API-NRC', full_name='Private Person', previous_company=company)
        RiskRecord.objects.create(employee=employee, risk_level='BLACK', reason='Public', is_public=True)
        RiskRecord.objects.create(employee=employee, risk_level='YELLOW', reason='Private', is_public=False)

    def test_public_api_only_returns_public_risk_records(self):
        response = self.api.get('/api/risk-records/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_employee_api_requires_admin(self):
        self.api.force_authenticate(self.user)
        self.assertEqual(self.api.get('/api/employees/').status_code, 403)

    def test_authenticated_api_verification(self):
        self.api.force_authenticate(self.user)
        response = self.api.post('/api/verifications/', {'employee_id': 'UNKNOWN', 'nrc_no': 'UNKNOWN', 'previous_company': '', 'consent_confirmed': True})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Verification.objects.get().result.risk_level, 'GREEN')

# Create your tests here.
