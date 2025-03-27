from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Survey, Question, Response, Choice, SubSection
from django.db.models import Min
from itertools import groupby
from django.utils import timezone
from django_jalali.db import models as jmodels
import jdatetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from bidi.algorithm import get_display
import arabic_reshaper
import os
import pytz

# Register Persian font
FONT_PATH = os.path.join(os.path.dirname(__file__), 'static', 'fonts', 'Vazir.ttf')

def reshape_persian_text(text):
    """Reshape Persian text for proper display"""
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def get_tehran_time():
    """Get current time in Tehran timezone"""
    tehran_tz = pytz.timezone('Asia/Tehran')
    return timezone.localtime(timezone.now(), tehran_tz)

@login_required
def get_jalali_datetime(request):
    now = get_tehran_time()
    jalali_datetime = jdatetime.datetime.fromgregorian(datetime=now)
    return JsonResponse({
        'datetime': jalali_datetime.strftime('%Y/%m/%d %H:%M:%S')
    })

@login_required
def export_pdf(request, survey_id, section):
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Check if user is assigned to this survey
    if not survey.assigned_users.filter(id=request.user.id).exists():
        messages.error(request, 'شما مجاز به دسترسی به این نظرسنجی نیستید')
        return redirect('survey_sections')

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    try:
        # Register Vazir font if available
        pdfmetrics.registerFont(TTFont('Vazir', FONT_PATH))
        font_name = 'Vazir'
    except:
        # Fallback to built-in font if Vazir is not available
        font_name = 'Helvetica'

    # Set initial font
    p.setFont(font_name, 14)
    
    # Add title
    title = reshape_persian_text(survey.title)
    p.drawRightString(width - 20, height - 40, title)
    
    # Add section info
    p.setFont(font_name, 12)
    section_text = reshape_persian_text(f"بخش: {dict(Survey.SECTION_CHOICES)[section]}")
    p.drawRightString(width - 20, height - 60, section_text)
    
    # Add datetime with Tehran timezone
    now = get_tehran_time()
    jalali_datetime = jdatetime.datetime.fromgregorian(datetime=now)
    date_text = reshape_persian_text(f"تاریخ: {jalali_datetime.strftime('%Y/%m/%d %H:%M:%S')}")
    p.drawRightString(width - 20, height - 80, date_text)
    
    # Get responses for this survey and user
    responses = Response.objects.filter(
        survey=survey,
        user=request.user,
        question__survey__section=section
    ).select_related('question', 'question__subsection')
    
    y_position = height - 120
    current_subsection = None
    
    for response in responses:
        # Check if we need to start a new page
        if y_position < 100:
            p.showPage()
            p.setFont(font_name, 12)
            y_position = height - 40
        
        # Add subsection header if changed
        if response.question.subsection != current_subsection:
            current_subsection = response.question.subsection
            if current_subsection:
                p.setFont(font_name, 12)
                subsection_text = reshape_persian_text(current_subsection.get_title_display())
                p.drawRightString(width - 20, y_position, subsection_text)
                y_position -= 20
        
        # Add question
        p.setFont(font_name, 10)
        question_text = reshape_persian_text(response.question.text)
        p.drawRightString(width - 40, y_position, question_text)
        y_position -= 20
        
        # Add response
        if response.question.question_type == 'text':
            if response.answer_text:
                answer_text = reshape_persian_text(f"پاسخ: {response.answer_text}")
                p.drawRightString(width - 60, y_position, answer_text)
        else:
            choices = [choice.text for choice in response.selected_choices.all()]
            if choices:
                choices_text = reshape_persian_text(f"پاسخ: {', '.join(choices)}")
                p.drawRightString(width - 60, y_position, choices_text)
            
            if response.comments:
                y_position -= 20
                comments_text = reshape_persian_text(f"توضیحات: {response.comments}")
                p.drawRightString(width - 60, y_position, comments_text)
        
        y_position -= 40
    
    p.showPage()
    p.save()
    
    # FileResponse sets the Content-Disposition header
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"survey_{survey.id}_{section}_{request.user.username}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@login_required
def survey_sections(request):
    # Get all surveys assigned to the user
    user_surveys = Survey.objects.filter(assigned_users=request.user)
    
    # Filter surveys by section
    section1_surveys = user_surveys.filter(section='section1').order_by('created_at')
    section2_surveys = user_surveys.filter(section='section2').order_by('created_at')
    
    context = {
        'section1_surveys': section1_surveys,
        'section2_surveys': section2_surveys,
    }
    
    return render(request, 'surveys/sections.html', context)

@login_required
def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Check if user is assigned to this survey
    if not survey.assigned_users.filter(id=request.user.id).exists():
        messages.error(request, 'شما مجاز به دسترسی به این نظرسنجی نیستید')
        return redirect('survey_sections')
    
    # Get all questions for the survey
    questions = survey.questions.select_related('subsection').order_by('subsection__order', 'subsection__id', 'order').all()
    
    if not questions:
        messages.warning(request, 'این نظرسنجی هنوز سوالی ندارد.')
        return redirect('survey_sections')
    
    # Organize questions by subsection
    questions_by_subsection = {}
    questions_without_subsection = []
    
    for question in questions:
        if question.subsection:
            if question.subsection not in questions_by_subsection:
                questions_by_subsection[question.subsection] = []
            questions_by_subsection[question.subsection].append(question)
        else:
            questions_without_subsection.append(question)
    
    context = {
        'survey': survey,
        'questions_by_subsection': questions_by_subsection,
        'questions_without_subsection': questions_without_subsection,
    }
    
    return render(request, 'surveys/survey_detail.html', context)

@login_required
def submit_survey(request, survey_id):
    if request.method != 'POST':
        return redirect('survey_sections')
        
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Check if user is assigned to this survey
    if not survey.assigned_users.filter(id=request.user.id).exists():
        messages.error(request, 'شما مجاز به دسترسی به این نظرسنجی نیستید')
        return redirect('survey_sections')
    
    questions = survey.questions.all()
    
    # Delete previous responses if any
    Response.objects.filter(user=request.user, survey=survey).delete()
    
    # Process each question's response
    for question in questions:
        response_key = f'question_{question.id}'
        comment_key = f'comment_{question.id}'
        
        if question.question_type == 'text':
            answer_text = request.POST.get(response_key, '').strip()
            if answer_text:
                Response.objects.create(
                    user=request.user,
                    survey=survey,
                    question=question,
                    answer_text=answer_text
                )
        else:
            choice_ids = request.POST.getlist(response_key)
            if choice_ids:
                # Get optional comment for single-choice questions
                comments = request.POST.get(comment_key, '').strip() if question.question_type == 'single' else ''
                
                response = Response.objects.create(
                    user=request.user,
                    survey=survey,
                    question=question,
                    comments=comments
                )
                response.selected_choices.set(choice_ids)
    
    # Store completion time and section in session with Tehran timezone
    completion_time = get_tehran_time()
    jalali_completion_time = jdatetime.datetime.fromgregorian(datetime=completion_time)
    formatted_time = jalali_completion_time.strftime('%Y/%m/%d %H:%M:%S')
    
    # Initialize completed_surveys in session if it doesn't exist
    if 'completed_surveys' not in request.session:
        request.session['completed_surveys'] = {}
    
    # Store survey completion info
    request.session['completed_surveys'][str(survey.id)] = {
        'completion_time': formatted_time,
        'section': survey.section
    }
    request.session.modified = True
    
    messages.success(
        request, 
        f'پاسخ‌های شما با موفقیت ثبت شد. زمان تکمیل: {formatted_time}. '
        'شما می‌توانید فایل PDF پاسخ‌های خود را از صفحه اصلی دانلود کنید.'
    )
    
    return redirect('survey_sections')
