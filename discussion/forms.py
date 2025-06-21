from django import forms
from .models import Discussion, Reply

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title...'}),
            'content': forms.Textarea(attrs={'placeholder': 'Content...', 'rows': 4}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Share your thoughts', 'rows': 3}),
        }
