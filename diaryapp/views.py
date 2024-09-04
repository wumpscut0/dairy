from logging import getLogger

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView, LogoutView, logout_then_login
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import classonlymethod
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from diaryapp.forms import CustomUserCreationForm

logger = getLogger("stdout")


class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "diaryapp/register.html"
    success_url = reverse_lazy("diaryapp:index")
    
    @classonlymethod
    def as_view(cls, **initkwargs):
        return login_not_required(super().as_view(**initkwargs))
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class CustomLoginView(LoginView):
    template_name = "diaryapp/login.html"
    redirect_authenticated_user = True
    success_url_allowed_hosts = "127.0.0.1", "localhost"

class CustomLogoutView(LogoutView):
    template_name = "diaryapp/logout.html"


# if self.status in ("failed", "done"):
#     self.over_at = now()
#
# settings.scheduler.add_job(reaper, "date", id=f"Target_{self.pk}", run_date=self.planned_datetime, args=[self.pk],
#                            replace_existing=True)

# @login_not_required
# def login_view(request: HttpRequest):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             next_ = request.POST.get("next")
#             if next_ is not None:
#                 redirect(next_)
#             else:
#                 redirect(reverse("diaryapp:index"))
#         else:
#             return render(request, "diaryapp:login.html", context={
#                 "error": "Wrong username or password",
#                 "username": username,
#                 "password": password,
#             })
#     elif request.method == "GET":
#         if not request.user.is_authenticated:
#             return render(request, "diaryapp:login.html")
#         else:
#             redirect(reverse("diaryapp:index"))

@login_not_required
def index(request: HttpRequest):
    return render(request, "diaryapp/index.html")

def diary(request: HttpRequest):
    ...
    