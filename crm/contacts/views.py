
from django.shortcuts import render, redirect
from api.crm import get_all_users, User


def index(request):
    return render(request, "contacts/index.html", context={
        "users": get_all_users()
    })


def add_contact(request):
    new_user = User(**dict(request.POST))
    print(request.POST["phone_number"])
    print(request.POST["phone_number"])
    new_user.save(True)

    return redirect('index')
