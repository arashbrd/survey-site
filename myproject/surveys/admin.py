from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from .models import Survey, Question, Choice, Response, SubSection
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin

# Unregister the Group model from admin
admin.site.unregister(Group)

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register our custom UserAdmin
@admin.register(User)
class CustomUserAdmin(ModelAdminJalaliMixin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('تاریخ‌های مهم', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_date_joined_jalali')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'date_joined')

    def get_date_joined_jalali(self, obj):
        return datetime2jalali(obj.date_joined).strftime('%Y/%m/%d %H:%M:%S')
    get_date_joined_jalali.short_description = 'تاریخ عضویت'
    get_date_joined_jalali.admin_order_field = 'date_joined'

class SubSectionInline(admin.TabularInline):
    model = SubSection
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('subsection', 'text', 'question_type', 'order')

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'created_at', 'get_response_count', 'get_actions_buttons')
    list_filter = ('section', 'created_at')
    search_fields = ('title',)
    inlines = [SubSectionInline, QuestionInline]
    filter_horizontal = ('assigned_users',)

    def get_response_count(self, obj):
        return Response.objects.filter(survey=obj).count() // max(obj.questions.count(), 1)
    get_response_count.short_description = 'تعداد پاسخ‌ها'

    def get_actions_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">مشاهده گزارش</a>&nbsp;'
            '<a class="button" href="{}">دانلود CSV</a>',
            f'/admin/surveys/survey/{obj.pk}/report/',
            f'/admin/surveys/survey/{obj.pk}/export/'
        )
    get_actions_buttons.short_description = 'گزارش‌ها'
    get_actions_buttons.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:survey_id>/report/', 
                 self.admin_site.admin_view(self.survey_report_view), 
                 name='survey-report'),
            path('<int:survey_id>/export/', 
                 self.admin_site.admin_view(self.export_responses), 
                 name='survey-export'),
        ]
        return custom_urls + urls

    def survey_report_view(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)
        questions = survey.questions.all()
        responses_data = []

        for question in questions:
            response_data = {
                'question': question.text,
                'type': question.question_type,
                'responses': []
            }

            if question.question_type == 'text':
                text_responses = Response.objects.filter(
                    question=question
                ).values_list('answer_text', flat=True)
                response_data['responses'] = list(text_responses)
            else:
                choice_counts = Choice.objects.filter(
                    question=question
                ).annotate(
                    response_count=Count('response')
                )
                for choice in choice_counts:
                    response_data['responses'].append({
                        'choice': choice.text,
                        'count': choice.response_count
                    })

            responses_data.append(response_data)

        context = {
            'survey': survey,
            'responses_data': responses_data,
            'opts': self.model._meta,
        }
        return render(request, 'admin/surveys/survey/report.html', context)

    def export_responses(self, request, survey_id):
        survey = Survey.objects.get(id=survey_id)
        csv_response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        csv_response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses_{timezone.now().date()}.csv"'
        
        # Add BOM for Excel to detect UTF-8
        csv_response.write('\ufeff')
        
        writer = csv.writer(csv_response)
        questions = survey.questions.all()
        
        # Write header
        header = ['کاربر', 'تاریخ ثبت']
        for question in questions:
            header.append(question.text)
        writer.writerow(header)
        
        # Get unique users who responded to this survey
        users_with_responses = Response.objects.filter(
            survey=survey
        ).values_list('user', flat=True).distinct()
        
        # Write data rows
        for user_id in users_with_responses:
            row = []
            responses = Response.objects.filter(
                survey=survey,
                user_id=user_id
            ).select_related('user', 'question')
            
            if responses.exists():
                row.append(responses[0].user.username)
                row.append(str(responses[0].created_at.date()))  # Convert date to string
                
                for question in questions:
                    response = responses.filter(question=question).first()
                    if response:
                        if question.question_type == 'text':
                            row.append(response.answer_text or '')  # Handle None values
                        else:
                            choices = response.selected_choices.all()
                            row.append(', '.join([c.text for c in choices]))
                    else:
                        row.append('')
                        
                writer.writerow(row)
        
        return csv_response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'subsection', 'question_type', 'order')
    list_filter = ('survey', 'subsection', 'question_type')
    search_fields = ('text',)
    inlines = [ChoiceInline]

@admin.register(SubSection)
class SubSectionAdmin(admin.ModelAdmin):
    list_display = ('get_title_display', 'survey', 'order')
    list_filter = ('survey', 'title')
    ordering = ['survey', 'order']

@admin.register(Response)
class ResponseAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('user', 'survey', 'question', 'created_at')
    list_filter = ('survey', 'user', 'created_at')
    search_fields = ('user__username', 'survey__title', 'question__text')
    readonly_fields = ('created_at',)
