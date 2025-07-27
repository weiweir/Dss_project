# business_match/urls.py
from django.urls import path
from . import views

app_name = 'business_match'

urlpatterns = [
    path('', views.match_view, name='match'),
   # path('api/sensitivity-analysis/', views.sensitivity_analysis_api, name='sensitivity_analysis'),
    path('api/detailed-analysis/<str:business_id>/', views.detailed_analysis_api, name='detailed_analysis'),
    path('export-report/<str:format_type>/', views.export_report, name='export_report'),
]