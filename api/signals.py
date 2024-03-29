# In your Django app's signals.py or any other appropriate module

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from djoser.signals import user_registered

@receiver(user_registered)
def assign_default_group(sender, user, request, **kwargs):
    # Assuming 'customer' is the name of the group
    group, created = Group.objects.get_or_create(name='Customer')
    user.groups.add(group)
