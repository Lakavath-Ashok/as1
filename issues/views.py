from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Complaint
from .forms import ComplaintForm, StudentSignUpForm


def home(request):
    return render(request, 'issues/home.html')


# ----------------- Complaint List -----------------
def complaint_list(request):
    complaints = Complaint.objects.all().order_by("-created_at")
    paginator = Paginator(complaints, 10)  # show 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "issues/complaints/list.html", {"page_obj": page_obj})


# ----------------- Create Complaint -----------------
@login_required
def create_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.reporter = request.user
            comp.status = "open"
            comp.save()
            return redirect("issues:my_complaints")
    else:
        form = ComplaintForm()
    return render(request, "issues/create_complaint.html", {"form": form})


# ----------------- My Complaints -----------------
@login_required
def my_complaints(request):
    qs = Complaint.objects.filter(reporter=request.user).order_by("-created_at")
    return render(request, "issues/my_complaints.html", {"complaints": qs})


# ----------------- View Complaint -----------------
@login_required
def view_complaint(request, pk):
    comp = get_object_or_404(Complaint, pk=pk)
    # Only reporter or staff can view
    if request.user != comp.reporter and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this complaint.")
        return redirect("issues:my_complaints")

    if request.user == comp.reporter and not comp.is_read_by_reporter:
        comp.is_read_by_reporter = True
        comp.save()

    return render(request, "issues/view_complaint.html", {"comp": comp})


# ----------------- Search -----------------
@login_required
def search(request):
    q = request.GET.get("q", "").strip()
    results = Complaint.objects.none()
    if q:
        results = Complaint.objects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(category__icontains=q)
        ).order_by("-created_at")
    return render(request, "issues/search_results.html", {"results": results, "q": q})


# ----------------- Unread Count API -----------------
@login_required
def unread_count_api(request):
    unread = Complaint.objects.filter(
        reporter=request.user, is_read_by_reporter=False
    ).count()
    return JsonResponse({"unread": unread})


# ----------------- Admin Helpers -----------------
def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
def admin_complaints(request):
    qs = Complaint.objects.all().order_by("-created_at")
    q = request.GET.get("q")
    status = request.GET.get("status")
    priority = request.GET.get("priority")

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(reporter__username__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)

    paginator = Paginator(qs, 20)  # paginate admin view
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "issues/admin_complaints.html", {"page_obj": page_obj})


@user_passes_test(is_staff)
def admin_update_complaint(request, pk):
    comp = get_object_or_404(Complaint, pk=pk)
    if request.method == "POST":
        comp.status = request.POST.get("status", comp.status)
        comp.priority = request.POST.get("priority", comp.priority)
        comp.admin_comment = request.POST.get("admin_comment", comp.admin_comment)
        comp.is_read_by_reporter = False
        comp.save()
        messages.success(request, "Complaint updated")
        return redirect("issues:admin_complaints")
    return render(request, "issues/admin_update_complaint.html", {"comp": comp})


# ----------------- Auth Views -----------------
def signup_view(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("issues:dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentSignUpForm()
    return render(request, "issues/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("issues:dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "issues/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("issues:login")


@login_required
def dashboard(request):
    # Summary counts for the logged-in user
    my_count = Complaint.objects.filter(reporter=request.user).count()
    open_count = Complaint.objects.filter(reporter=request.user, status='open').count()
    # high_pending: high priority that are not resolved
    high_pending = Complaint.objects.filter(
        reporter=request.user,
        priority='high'
    ).exclude(status='resolved').count()
    unread = Complaint.objects.filter(
        reporter=request.user, is_read_by_reporter=False
    ).count()
    # recent reports (most recent 5)
    recent = Complaint.objects.filter(reporter=request.user).order_by('-created_at')[:5]

    return render(request, "issues/dashboard.html", {
        "my_count": my_count,
        "open_count": open_count,
        "high_pending": high_pending,
        "unread": unread,
        "recent": recent,
    })