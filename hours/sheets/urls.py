from django.urls import path
from . import views, api_views, login_views

app_name = 'sheets'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),

    path('signup', login_views.signup, name='signup'),
    path('login', login_views.login, name='login'),
    path('change_password', login_views.change_password, name='change_password'),
    path('logout', login_views.logout, name='logout'),

    path('hours', views.HoursView.as_view(), name='hours'),
    path('info', views.InfoView.as_view(), name='info'),
    path('api/projects', api_views.ProjectListApiView.as_view(), name='api_projects'),
    path('api/info', api_views.InfoApiView.as_view(), name='api_info'),
    path('api/sheets/<str:year>/<str:month>', api_views.SheetApiView.as_view(), name='api_sheets'),
]
