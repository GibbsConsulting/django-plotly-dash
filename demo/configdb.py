#!/usr/bin/env python
#
# Create a new superuser
from django.contrib.auth import get_user_model

UserModel = get_user_model()

name="admin"
password="admin"

try:
    UserModel.objects.get(username=name)
except:
    su = UserModel.objects.create_user(name,password=password)
    su.is_staff=True
    su.is_superuser=True
    su.save()
