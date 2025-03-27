from django.conf import settings

def copyright_info(request):
    return {
        'COPYRIGHT_TEXT': settings.COPYRIGHT_TEXT,
        'COPYRIGHT_LINK': settings.COPYRIGHT_LINK,
        'COPYRIGHT_COMPANY': settings.COPYRIGHT_COMPANY,
    } 