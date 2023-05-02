from django.forms import *
from .models import User

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['persona','user_id', 'first_name', 'last_name', 'username', 'language_code', 'is_bot']


class MessageForm(Form):

    message = CharField(max_length=100)
    message.widget.attrs.update({'class':'form-control'})