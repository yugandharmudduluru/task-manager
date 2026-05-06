from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('logout/', views.logout_view, name="logout"),

    path('dashboard/', views.dashboard, name="dashboard"),

    path('projects/', views.projects, name="projects"),
    path('create-project/', views.create_project, name="create_project"),
    path('project/<int:project_id>/', views.project_detail, name="project_detail"),

    path('tasks/', views.tasks, name="tasks"),
    path('create-task/', views.create_task, name="create_task"),
    path('update-task/<int:task_id>/', views.update_task_status, name="update_task_status"),
    path('delete-task/<int:task_id>/', views.delete_task, name="delete_task"),
]