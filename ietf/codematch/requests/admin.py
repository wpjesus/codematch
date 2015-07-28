from django.contrib import admin

# Register your models here.

from .models import CodeRequest

admin.site.register(CodeRequest)
