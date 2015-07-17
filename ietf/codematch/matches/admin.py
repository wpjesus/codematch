from django.contrib import admin

# Register your models here.

from .models import ProjectContainer, CodingProject

admin.site.register(ProjectContainer)
admin.site.register(CodingProject)
