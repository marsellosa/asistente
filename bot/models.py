from django.db.models import * #type:ignore
from django.urls import reverse
from persona.models import Persona

class User(Model):
    user_id = CharField(max_length=200, unique=True) #user_id
    first_name = CharField(max_length=200, null=True, blank=True)
    last_name = CharField(max_length=200, null=True, blank=True)
    username = CharField(max_length=200, null=True, blank=True)
    is_bot = BooleanField(default=False)
    persona = OneToOneField(Persona, on_delete=SET_NULL, null=True, blank=True)
    language_code = CharField(max_length=8, null=True, blank=True)
    inserted_on = DateTimeField(auto_now_add=True)

    def send_message(self):
        return reverse('bot:send_message', kwargs={'user_id' : self.user_id })
    
    def get_user_requests(self):
        qs = self.activity_set.order_by('-inserted_on')[:15] #type:ignore
        return reversed(list(qs))
    
    def __str__(self):
        # return self.user_id
        return f"{self.first_name} {self.last_name}"

class Activity(Model):
    user = ForeignKey('User', on_delete=CASCADE)
    text = CharField(max_length=255, blank=True, null=True)
    inserted_on = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'

    def __str__(self):
        return str(self.user)
    