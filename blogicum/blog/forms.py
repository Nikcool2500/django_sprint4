from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title",
                  "text",
                  "is_published", "pub_date", "location", "category", "image")
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M',
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
