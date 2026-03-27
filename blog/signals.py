"""
blog/signals.py

Django signals are "event listeners" — they automatically run code
when certain events happen (like saving a model).

Here we use:
  - post_save signal on the User model
  - Automatically creates a UserProfile whenever a new User is registered
  - This is a common Django pattern called "extending the user model"
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler that fires AFTER a User is saved to the database.

    Parameters:
    - sender:   The model class that sent the signal (User)
    - instance: The actual User object that was saved
    - created:  True if this is a NEW user (not an update)
    - **kwargs: Extra arguments (always include this)

    Logic: Only create profile if this is a brand new user (created=True)
    This prevents creating duplicate profiles when a user is updated.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler that also saves the UserProfile whenever the User is saved.
    This keeps them in sync.

    If the user has a profile (most do), save it.
    If not (edge case), create one.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.get_or_create(user=instance)
