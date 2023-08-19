from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from django.contrib.auth.models import User, Group

@receiver(pre_save, sender=User)
def create_username(sender, instance, **kwargs):
    if not instance.username:
        instance.username = instance.email

@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get_or_create(name='socios')[0]
        user = User.objects.get(username=instance.username)
        user.groups.add(group)
