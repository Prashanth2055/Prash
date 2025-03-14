from django.contrib import admin
from .models import Contact, Blogs

# Register your models here.
@admin.register(Contact, Blogs)
class ContactInfo(admin.ModelAdmin):
    model = Contact, Blogs