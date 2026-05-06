from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import *


# ======================
# 🔐 SIGNUP
# ======================
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            messages.info(request, "Account already exists. Please login.")
            return redirect("login")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        profile, _ = Profile.objects.get_or_create(user=user)

        # First user becomes admin
        if User.objects.count() == 1:
            profile.role = "Admin"
            profile.save()

        messages.success(request, "Signup successful! Please login.")
        return redirect("login")

    return render(request, "signup.html")


# ======================
# 🔐 LOGIN
# ======================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {
            "error": "Invalid credentials or please signup"
        })

    return render(request, "login.html")


# ======================
# 🔓 LOGOUT
# ======================
def logout_view(request):
    logout(request)
    return redirect("login")


# ======================
# 📊 DASHBOARD
# ======================
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role == "Admin":
        tasks = Task.objects.all()
        projects = Project.objects.all()
        users = User.objects.all()

        context = {
            "is_admin": True,
            "total_projects": projects.count(),
            "total_members": users.count(),
            "total_tasks": tasks.count(),
            "completed": tasks.filter(status="DONE").count(),
            "pending": tasks.filter(status="TODO").count(),
            "overdue": tasks.filter(
                due_date__lt=now().date(),
                status__in=["TODO", "IN_PROGRESS"]
            ).count(),
            "tasks": tasks.order_by("-id")[:5]
        }

    else:
        tasks = Task.objects.filter(assigned_to=request.user)

        context = {
            "is_admin": False,
            "total_tasks": tasks.count(),
            "completed": tasks.filter(status="DONE").count(),
            "pending": tasks.filter(status="TODO").count(),
            "overdue": tasks.filter(
                due_date__lt=now().date(),
                status__in=["TODO", "IN_PROGRESS"]
            ).count(),
            "tasks": tasks.order_by("-id")[:5]
        }

    return render(request, "dashboard.html", context)


# ======================
# 📁 PROJECT LIST
# ======================
def projects(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role == "Admin":
        projects = Project.objects.all()
    else:
        # projects = Project.objects.filter(members__user=request.user.id)
        projects = Project.objects.filter(members=request.user)

    return render(request, "projects.html", {
        "projects": projects,
        "is_admin": profile.role == "Admin"
    })


# ======================
# ➕ CREATE PROJECT
# ======================
def create_project(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role != "Admin":
        return redirect("projects")

    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        member_ids = request.POST.getlist("members")

        project = Project.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )

        # ✅ Add admin
        project.members.add(request.user)

        # ✅ Add selected members
        if member_ids:
            selected_users = User.objects.filter(id__in=member_ids)
            project.members.add(*selected_users)

        return redirect("projects")

    return render(request, "create_project.html", {
        "users": users
    })


# ======================
# 📋 TASK LIST
# ======================
def tasks(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role == "Admin":
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    return render(request, "tasks.html", {"tasks": tasks})


# ======================
# 🔄 UPDATE TASK
# ======================
@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # 🔐 Permission check
    if task.assigned_to != request.user:
        return redirect("tasks")

    if request.method == "POST":
        status = request.POST.get("status")

        # 🛑 Prevent None or empty value
        if not status:
            return render(request, "update_task.html", {
                "task": task,
                "error": "Status is required"
            })

        task.status = status
        task.save()
        return redirect("tasks")

    # ✅ GET request → show form
    return render(request, "update_task.html", {"task": task})



# ======================
# ❌ DELETE TASK
# ======================
def delete_task(request, task_id):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.role != "Admin":
        return redirect("tasks")

    task = get_object_or_404(Task, id=task_id)
    task.delete()

    return redirect("tasks")

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # ✅ Check access (ManyToMany way)
    if request.user not in project.members.all() and request.user != project.created_by:
        return redirect("projects")

    # ✅ Get tasks
    tasks = project.tasks.all()

    # ✅ Get members
    members = project.members.all()

    return render(request, "project_detail.html", {
        "project": project,
        "tasks": tasks,
        "members": members
    })

@login_required
def create_task(request):
    # ✅ Role check without get_role
    if request.user.profile.role != "Admin":
        return render(request, "create_task.html", {
            "error": "You are not allowed to create tasks"
        })

    if request.method == "POST":
        title = request.POST.get("title")

        if not title:
            return render(request, "create_task.html", {
                "error": "Title is required"
            })

        Task.objects.create(
            title=title,
            description=request.POST.get("description"),
            project_id=request.POST.get("project"),
            assigned_to_id=request.POST.get("assigned_to"),
            status=request.POST.get("status"),
            due_date=request.POST.get("due_date")
        )

        return redirect("/tasks/")

    return render(request, "create_task.html", {
        "projects": Project.objects.all(),
        "users": User.objects.all()
    })