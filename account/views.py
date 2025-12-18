from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CompanyForm
from django.contrib.auth.decorators import login_required
import uuid
from .forms import SuperAdminForm
from .models import Company
from .services import send_activation_email
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from .models import SubscriptionPlan
from django.utils import timezone


# ==== admin platform login ====
@login_required
def platform_dashboard(request):
    if not request.user.is_superuser:
        return redirect("account:platform-login")
    
    plans = SubscriptionPlan.objects.all()
    companies = Company.objects.all()

     # Filters
    status_filter = request.GET.get("status")
    plan_filter = request.GET.get("plan")

    if plan_filter:
        companies = companies.filter(subscription_plan_id=plan_filter)

    if status_filter:
        today = timezone.now().date()
        if status_filter == "ACTIVE":
            companies = companies.filter(license_end_date__gte=today)
        elif status_filter == "EXPIRED":
            companies = companies.filter(license_end_date__lt=today)

    context = {
        "plans": plans,
        "companies": companies
    }

    return render(request, "account/platform_dashboard.html", context)

    # return render(
    #     request,
    #     "account/platform_dashboard.html",
    #     {
    #         "plans": plans,
    #         "companies": companies
    #     }
    # )
    #return render(request, "account/platform_dashboard.html")

def platform_login(request):
    # اذا مسجل دخول ينقله لصفحة الدشبورد للبلاتفورم 
    # if request.user.is_authenticated and request.user.is_superuser:
    #     return redirect("account:platform-dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect("account:platform-dashboard")

        return render(request, "account/login.html", {
            "error": "Invalid email or password"
        })

    return render(request, "account/login.html")

# ==== admin platform create company ====
@login_required
def create_company(request):
    if not request.user.is_superuser:
        return redirect("account:platform-login")

    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            # company = form.save()
            company = form.save(commit=False)
            company.save()
            # create superadmin for company
            return redirect("account:create-super-admin", company_id=company.id)
    else:
        form = CompanyForm()

    return render(request, "account/create_company.html", {"form": form})

@login_required
def create_super_admin(request, company_id):
    if not request.user.is_superuser:
        return redirect("account:platform-login")

    company = get_object_or_404(Company, id=company_id)

    if request.method == "POST":
        form = SuperAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "COMPANY_ADMIN"
            user.company = company
            user.is_active = False
            user.set_unusable_password()
            user.activation_token = uuid.uuid4()
            user.save()

            send_activation_email(user)

            return render(request, "account/super_admin_created.html", {
                "email": user.email
            })
    else:
        form = SuperAdminForm()

    return render(request, "account/create_super_admin.html", {
        "form": form,
        "company": company
    })

# ==== Logout =====
def logout_view(request):
    logout(request)
    return redirect("account:platform-login")

