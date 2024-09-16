from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Ticket, Review

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']


class FollowUserForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
