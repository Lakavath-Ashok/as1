from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    admin_comment = models.TextField(blank=True)
    is_read_by_reporter = models.BooleanField(default=True)  # notifications

    def __str__(self):
        return f"{self.title} ({self.reporter.username})"