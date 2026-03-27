"""
blog/forms.py

Forms handle user input validation and rendering.
Django forms map directly to HTML <form> elements.

Forms in this file:
  1. PostForm             — Create/edit a blog post
  2. CommentForm          — Submit a comment
  3. UserRegistrationForm — Register a new user account
  4. UserUpdateForm       — Update basic User fields (name, email)
  5. UserProfileForm      — Update extended profile fields (bio, avatar, etc.)
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post, Comment, UserProfile


# ─────────────────────────────────────────────
# 1. POST FORM
# ─────────────────────────────────────────────
class PostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts.
    ModelForm automatically creates form fields from the Post model.
    """

    # Override the 'content' field to use CKEditor's rich text widget
    # Without this, it would just be a plain <textarea>
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post  # Which model this form maps to
        # Which fields to include (in order they appear in the form)
        fields = [
            'title',
            'excerpt',
            'category',
            'tags',
            'content',
            'thumbnail',
            'status',
            'featured',
        ]
        # widgets: customize how each field is rendered as HTML
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter an engaging post title...',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short summary (leave blank to auto-generate)...',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'python, django, web-dev (comma separated)',
                'data-role': 'tagsinput',
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text to fields
        self.fields['tags'].help_text = 'Enter tags separated by commas'
        self.fields['featured'].help_text = 'Featured posts appear on the homepage hero section'


# ─────────────────────────────────────────────
# 2. COMMENT FORM
# ─────────────────────────────────────────────
class CommentForm(forms.ModelForm):
    """
    Simple form for submitting a comment on a post.
    """
    class Meta:
        model = Comment
        fields = ['body']  # Only show the body field (author & post set in view)
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts...',
            }),
        }
        labels = {
            'body': '',  # Hide the label (we use placeholder instead)
        }


# ─────────────────────────────────────────────
# 3. USER REGISTRATION FORM
# ─────────────────────────────────────────────
class UserRegistrationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm.
    UserCreationForm already handles:
      - username
      - password1 (password)
      - password2 (confirm password)
      - password validation and matching

    We add: email, first_name, last_name
    """

    # Add email as a REQUIRED field (it's optional in Django by default)
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Add our new fields alongside the inherited fields
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap CSS classes to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })

    def save(self, commit=True):
        """
        Override save() to also store email, first_name, last_name.
        The parent UserCreationForm.save() only saves username & password.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────
# 4. USER UPDATE FORM
# ─────────────────────────────────────────────
class UserUpdateForm(forms.ModelForm):
    """
    Allows users to update their basic Django User fields.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


# ─────────────────────────────────────────────
# 5. USER PROFILE FORM
# ─────────────────────────────────────────────
class UserProfileForm(forms.ModelForm):
    """
    Allows users to update their extended profile (bio, avatar, social links).
    """
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website', 'twitter', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell readers about yourself...',
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com',
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@yourtwitterhandle',
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'linkedin.com/in/yourprofile',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
