from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'reporter', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'description', 'reporter__username')