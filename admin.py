from django.contrib import admin

# Register your models here.

from .models import ProjectContainer, CodeRequest, CodingProject

admin.site.register(ProjectContainer)
admin.site.register(CodeRequest)
admin.site.register(CodingProject)
