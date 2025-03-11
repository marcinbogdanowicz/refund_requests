from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile_for_superusers(sender, instance, created, **kwargs):
    if (
        created
        and instance.is_superuser
        and not hasattr(instance, 'userprofile')
    ):
        UserProfile.objects.create(user=instance)
