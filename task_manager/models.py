from django.db import models
from django.contrib.auth.models import User


# 👤 USER PROFILE (GLOBAL ROLE)
class Profile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Member', 'Member')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="Member")

    def __str__(self):
        return self.user.username


# 📁 PROJECT
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="projects")  # ✅ important
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


# 📋 TASK
class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'TODO'),
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('DONE', 'DONE'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
