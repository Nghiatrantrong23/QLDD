from django.shortcuts import render

from django.core.mail import send_mail
from django.http import HttpResponse

from django.core.mail import send_mail
from django.http import HttpResponse

def send_example_email(request):
    try:        
        send_mail(
            subject='Email from Django',
            message='This is an email sent from Django application.',
            from_email='example@your_mailtrap_domain',
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        
        return HttpResponse('Email sent successfully!')
    except Exception as e:
        return HttpResponse(f'Failed to send email: {str(e)}')