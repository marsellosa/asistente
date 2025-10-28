from django.http import HttpResponse
from django.shortcuts import render
from twilio.rest import Client
from decouple import config
from django.views.decorators.csrf import csrf_exempt

def messages_view(request):
    # Your Twilio credentials
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    messages = client.messages.list(limit=20)

    context = {
        'messages': messages,
    }

    return render(request, 'whatsapp/messages.html', context)

@csrf_exempt
def response_message_view(request):
    if request.method == 'POST':
        # print(f"Received POST request with data: {request.POST}")
        # print(f"Received POST request with data: {request.POST['To'] if 'To' in request.POST else 'No To field'}")
        twilio_phone_number = request.POST.get('To')
        sender_number = request.POST.get('From')
        message_body = request.POST.get('Body')
        # print(f"Sending message to {sender_number}: {message_body}")
        # Your Twilio credentials
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        # twilio_phone_number = config('TWILIO_PHONE_NUMBER')


        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=sender_number
        )

        return HttpResponse(status=200)

    return render(request, 'whatsapp/send_message.html')


def send_message_view(request):
    if request.method == 'POST':
        # print(f"Received POST request with data: {request.POST}")
        to_number = request.POST.get('to_number')
        message_body = request.POST.get('message_body')
        # Your Twilio credentials
        account_sid = config('TWILIO_ACCOUNT_SID')
        auth_token = config('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)
        twilio_phone_number = config('TWILIO_PHONE_NUMBER')

        message = client.messages.create(
                body=message_body,
                from_=f'whatsapp:{twilio_phone_number}',
                to=f'whatsapp:{to_number}'
            )

        return HttpResponse(f"Message sent with SID: {message.sid}")