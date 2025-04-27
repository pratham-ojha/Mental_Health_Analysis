# chat/forms.py

from django import forms

class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Your message')
