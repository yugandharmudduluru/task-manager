from django.contrib import admin
from .models import Project, Task, Profile


# ======================
# PROJECT ADMIN
# ======================
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_by',)
    filter_horizontal = ('members',)   # ✅ for selecting users easily


# ======================
# TASK ADMIN
# ======================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'project', 'assigned_to', 'status', 'due_date')
    search_fields = ('title',)
    list_filter = ('status', 'project', 'assigned_to')


# ======================
# PROFILE ADMIN
# ======================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user__username',)
    list_filter = ('role',)