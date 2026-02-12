from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


from allauth.account.forms import SignupForm

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        # Lógica adicional si es necesaria
        return user
