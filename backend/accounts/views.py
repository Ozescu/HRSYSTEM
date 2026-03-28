from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm, UserRegistrationForm


def landing_page(request):
	return render(request, "accounts/landing.html")


def login_page(request):
	if request.user.is_authenticated:
		return redirect("landing")

	form = EmailAuthenticationForm(request, data=request.POST or None)
	if request.method == "POST" and form.is_valid():
		login(request, form.get_user())
		messages.success(request, "Welcome back to AIDEED.")
		return redirect("landing")

	return render(request, "accounts/login.html", {"form": form})


def register_page(request):
	if request.user.is_authenticated:
		return redirect("landing")

	form = UserRegistrationForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = form.save()
		login(request, user)
		messages.success(request, "Your account has been created successfully.")
		return redirect("landing")

	return render(request, "accounts/register.html", {"form": form})


def logout_page(request):
	if request.method == "POST":
		logout(request)
		messages.info(request, "You have been signed out.")
	return redirect("landing")
