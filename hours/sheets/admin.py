from django.contrib import admin
from django.contrib.auth.models import Group
from sheets.models import *

# Register your models here.
admin.site.register(Project)
admin.site.register(ProjectFamily)
admin.site.register(Sheet)

admin.site.unregister(Group)