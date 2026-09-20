from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('companies', views.CompanyViewSet)
router.register('employees', views.EmployeeViewSet)
router.register('cases', views.CaseViewSet, basename='case')
router.register('evidence', views.EvidenceViewSet, basename='evidence')
router.register('risk-records', views.RiskRecordViewSet, basename='riskrecord')
router.register('verifications', views.VerificationViewSet, basename='verification')
router.register('news', views.NewsViewSet, basename='news')
router.register('reports', views.ReportViewSet, basename='report')
router.register('appeals', views.AppealViewSet, basename='appeal')
router.register('audit-logs', views.AuditLogViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('black-list/', views.blacklist, name='blacklist'),
    path('companies/', views.companies, name='companies'),
    path('verification/', views.verification, name='verification'),
    path('verification/<uuid:reference>/', views.verification_result, name='verification_result'),
    path('warning-news/', views.news, name='news'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('appeal/', views.appeal, name='appeal'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
