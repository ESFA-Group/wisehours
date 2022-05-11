from email.policy import default
from django.db import models
from django.contrib.auth.models import User
import jdatetime as jdt

def current_year():
    return jdt.date.today().year

def current_month():
    return jdt.date.today().month

class Sheet(models.Model):
    user = models.ForeignKey(User, verbose_name="user", related_name="sheets", on_delete=models.CASCADE)
    year = models.PositiveIntegerField('year', default=current_year)
    month = models.PositiveIntegerField('month', default=current_month)
    data = models.JSONField(default=dict)