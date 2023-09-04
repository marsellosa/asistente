from django.forms import * #type:ignore
from .models import BotUser

class BotUserForm(ModelForm):

    class Meta:
        model = BotUser
        fields = ['persona','user_id', 'first_name', 'last_name', 'username', 'language_code', 'is_bot']


class MessageForm(Form):

    message = CharField(max_length=100)
    message.widget.attrs.update({'class':'form-control'})