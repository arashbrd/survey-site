from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_sections, name='survey_sections'),
    path('survey/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('survey/<int:survey_id>/submit/', views.submit_survey, name='submit_survey'),
    path('get_jalali_datetime/', views.get_jalali_datetime, name='get_jalali_datetime'),
    path('survey/<int:survey_id>/export_pdf/<str:section>/', views.export_pdf, name='export_pdf'),
] 