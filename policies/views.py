from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Policy, PolicyAudience, CompanyGroup, PolicyAcknowledgement
from django.contrib.auth.decorators import login_required



# def policy_list(request):
#     all_policies = Policy.objects.all().order_by('-created_at')

#     paginator = Paginator(all_policies, 6)  # 6 Policies فقط
#     page_number = request.GET.get('page')
#     policies = paginator.get_page(page_number)

#     return render(request, 'policy/policy.html', {
#         'policies': policies
#     })
@login_required
def policy_list(request):
    user = request.user

    if user.role == "EMPLOYEE":
        # سياسات خاصة بقروبات الموظف
        user_groups = user.company_groups.all()

        policies = Policy.objects.filter(
            is_published=True,
            groups__in=user_groups
        ).distinct()

    else:
        # Company Admin يشوف كل سياسات الشركة
        policies = Policy.objects.filter(is_published=True)

    paginator = Paginator(policies.order_by('-created_at'), 6)
    page_number = request.GET.get('page')
    policies = paginator.get_page(page_number)

    return render(request, 'policy/policy.html', {
        'policies': policies
    })

# def policy_detail(request, id):
#     policy = get_object_or_404(Policy, id=id)

    
#     acknowledgements = policy.acknowledgements.select_related('user')

#     return render(request, 'policy/policy_detail.html', {
#         'policy': policy,
#         'acknowledgements': acknowledgements
#     })

@login_required
def policy_detail(request, id):
    policy = get_object_or_404(Policy, id=id)

    if request.user.role != "COMPANY_ADMIN":
        return redirect("account:platform-login")

    acknowledgements = policy.acknowledgements.select_related('user')

    return render(request, 'policy/policy_detail.html', {
        'policy': policy,
        'acknowledgements': acknowledgements
    })



# def create_policy(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         group_id = request.POST.get('group')

#         policy = Policy.objects.create(
#             title=title,
#             description=description,
#             is_published=True
#         )

#         if group_id:
#             group = get_object_or_404(UserGroup, id=group_id)
#             PolicyAudience.objects.create(
#                 policy=policy,
#                 group=group
#             )

#         return redirect('policies:policy_list')  # ✅ رجوع لصفحة السياسات

#     groups = UserGroup.objects.all()
#     return render(request, 'policy/create_policy.html', {
#         'groups': groups
#     })

@login_required
def create_policy(request):
    if request.user.role != "COMPANY_ADMIN":
        return redirect("account:platform-login")

    company = request.user.company

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        group_ids = request.POST.getlist('groups')

        policy = Policy.objects.create(
            title=title,
            description=description,
            is_published=True
        )

        groups = CompanyGroup.objects.filter(
            id__in=group_ids,
            company=company
        )

        for group in groups:
            PolicyAudience.objects.create(
                policy=policy,
                group=group
            )

        return redirect('policies:policy_list')

    groups = CompanyGroup.objects.filter(company=company, is_system=False)
    return render(request, 'policy/create_policy.html', {
        'groups': groups
    })

# def policy_acknowledge(request, id):
#     policy = get_object_or_404(Policy, id=id)

#     acknowledged = False

#     if request.method == 'POST':
#         acknowledged = True
#         # هنا لاحقًا زميلاتك بيضيفون الحفظ في PolicyAcknowledgement

#     return render(request, 'policy/policy_acknow.html', {
#         'policy': policy,
#         'acknowledged': acknowledged
#     })


@login_required
def policy_acknowledge(request, id):
    policy = get_object_or_404(Policy, id=id)
    user = request.user

    # ❌ منع Company Admin
    if user.role != "EMPLOYEE":
        return redirect('policies:policy_list')

    already_acknowledged = PolicyAcknowledgement.objects.filter(
        policy=policy,
        user=user
    ).exists()

    if request.method == 'POST' and not already_acknowledged:
        PolicyAcknowledgement.objects.create(
            policy=policy,
            user=user
        )
        already_acknowledged = True

    return render(request, 'policy/policy_acknow.html', {
        'policy': policy,
        'acknowledged': already_acknowledged
    })


@login_required
def employee_policies(request):
    if request.user.role != "EMPLOYEE":
        return redirect("account:platform-login")

    user_groups = request.user.company_groups.all()

    policies = Policy.objects.filter(
        is_published=True,
        groups__in=user_groups
    ).distinct()

    return render(request, 'policy/employee_policy_list.html', {
        'policies': policies
    })