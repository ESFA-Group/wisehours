from django.urls import path
from . import views, api_views, login_views

app_name = 'sheets'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),

    path('signup', login_views.signup, name='signup'),
    path('login', login_views.login, name='login'),
    path('change_password', login_views.change_password, name='change_password'),
    path('logout', login_views.logout, name='logout'),

    path('info', views.InfoView.as_view(), name='info'),
    path('hours', views.HoursView.as_view(), name='hours'),
    path('reports', views.ReportsView.as_view(), name='reports'),
    path('detailed_report', views.DetailedReportView.as_view(), name='detailed_report'),
    path('api/info', api_views.InfoApiView.as_view(), name='api_info'),
    path('api/projects', api_views.ProjectListApiView.as_view(), name='api_projects'),
    path('api/sheets/<str:year>/<str:month>', api_views.SheetApiView.as_view(), name='api_sheets'),
    path('api/monthly_report/<str:year>/<str:month>', api_views.MonthlyReportApiView.as_view(), name='api_monthly_report'),
]
