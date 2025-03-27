from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels

class Survey(models.Model):
    SECTION_CHOICES = [
        ('section1', 'بخش اول'),
        ('section2', 'بخش دوم'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_surveys', blank=True, verbose_name='کاربران مجاز')
    
    def __str__(self):
        return self.title
        
    class Meta:
        permissions = [
            ("view_section1", "Can view section 1 surveys"),
            ("view_section2", "Can view section 2 surveys"),
        ]
        verbose_name = 'نظرسنجی'
        verbose_name_plural = 'نظرسنجی‌ها'

class SubSection(models.Model):
    SUBSECTION_CHOICES = [
        ('medical_center', 'مشخصات مرکز درمانی'),
        ('hospital_management', 'پایش مدیریتی بیمارستان'),
        ('emergency', 'پایش بخش اورژانس'),
        ('paraclinic', 'پایش بخش پاراکلینیک،بستری سرپایی'),
        ('other', 'غیره'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='subsections')
    title = models.CharField(max_length=200, verbose_name='عنوان زیربخش', choices=SUBSECTION_CHOICES)
    order = models.IntegerField(verbose_name='ترتیب')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'زیربخش'
        verbose_name_plural = 'زیربخش‌ها'
    
    def __str__(self):
        return f"{self.survey.title} - {self.get_title_display()}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('text', 'پاسخ متنی'),
        ('single', 'تک انتخابی'),
        ('multiple', 'چند انتخابی'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    subsection = models.ForeignKey(SubSection, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['subsection__order', 'order']
    
    def __str__(self):
        if self.subsection:
            return f"{self.survey.title} - {self.subsection.title} - سوال {self.order}"
        return f"{self.survey.title} - سوال {self.order}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    comments = models.TextField(verbose_name='توضیحات تکمیلی', blank=True, null=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'survey', 'question']
        verbose_name = 'پاسخ'
        verbose_name_plural = 'پاسخ‌ها'

    def __str__(self):
        return f'پاسخ {self.user.username} به {self.question.text}'
