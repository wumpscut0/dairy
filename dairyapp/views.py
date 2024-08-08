import datetime
from datetime import timedelta

from django.forms import BoundField, ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.utils.timezone import now

from .models import Quest, Origin, Day


class IndexTemplateView(TemplateView):
    template_name = "dairyapp/index.html"


class OriginCreateView(CreateView):
    model = Origin
    fields = "name", "origin", "status"
    success_url = reverse_lazy("dairyapp:origin_list")

    def get_initial(self):
        initial = super().get_initial()
        initial["status"] = "a"
        return initial


class OriginListView(ListView):
    queryset = Origin.objects.all()


class OriginUpdateView(UpdateView):
    model = Origin
    fields = "name", "status", "origin"
    success_url = reverse_lazy("dairyapp:origin_list")
    template_name = "dairyapp/origin_update_form.html"

    @staticmethod
    def _process_start_quest(origin_name: str):
        origin = Origin.objects.get(name=origin_name)
        Quest.objects.create(origin=origin)
        origin.last_extracted_at = now()
        origin.save()
        return redirect(reverse("dairyapp:quest_list"))

    def form_valid(self, form):
        origin_name = self.request.POST.get("origin_to_quest")
        if origin_name:
            return self._process_start_quest(origin_name)

        return super().form_valid(form)

    def form_invalid(self, form):
        origin_name = self.request.POST.get("origin_to_quest")
        if origin_name:
            return self._process_start_quest(origin_name)
        return super().form_invalid(form)


class QuestFormView(CreateView):
    model = Quest
    fields = "origin",
    template_name = 'dairyapp/quest_form.html'
    success_url = reverse_lazy("dairyapp:index")

    @staticmethod
    def _extract_actual_origin():
        new_origin = Origin.objects.filter(status="a", last_extracted_at=None).order_by("created_at").first()
        if new_origin:
            origin = new_origin
        else:
            origin = Origin.objects.filter(status="a").first()
        return origin

    def get(self, request, *args, **kwargs):
        origin = self._extract_actual_origin()
        if origin is None:
            return redirect(reverse("dairyapp:origin_list"))
        origin.last_extracted_at = now()
        origin.save()
        self.request.session["origin_pk"] = origin.pk
        self.extra_context = {"origin": origin}
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial["origin"] = Origin.objects.get(pk=self.request.session["origin_pk"])
        return initial


class QuestListView(ListView):
    model = Quest
    context_object_name = 'object_list'
    template_name = 'dairyapp/quest_list.html'
    delta_day = timedelta(days=1)

    def get_queryset(self):
        date = self.request.GET.get('date', now().date())
        if isinstance(date, str):
            date = datetime.datetime.fromisoformat(date).date()
        return Quest.objects.filter(created_at__date=date).select_related("origin").order_by("created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date', now().date())
        if isinstance(date, str):
            date = datetime.datetime.fromisoformat(date).date()
        day, created = Day.objects.get_or_create(created_at__date=date, defaults={"created_at": date})
        context['day'] = day
        context['date'] = date
        context['has_previous'] = Quest.objects.filter(created_at__date=date - self.delta_day).exists()
        context['has_next'] = Quest.objects.filter(created_at__date=date).exists()
        return context

    def get(self, request: HttpRequest, *args, **kwargs):
        date_str = request.GET.get('date')
        if date_str:
            date = datetime.datetime.fromisoformat(date_str).date()
        else:
            date = now().date()

        if 'previous' in request.GET:
            date -= self.delta_day
        elif 'next' in request.GET:
            date += self.delta_day

        request.GET = request.GET.copy()
        request.GET['date'] = date.isoformat()

        return super().get(request, *args, **kwargs)


class QuestUpdateView(UpdateView):
    model = Quest
    fields = "complete_description",
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("dairyapp:quest_list")
    context_object_name = "quest"

    # def get(self, request, *args, **kwargs):
    #     quest = Quest.objects.select_related("origin").get(pk=kwargs["pk"])
    #     self.extra_context = {
    #         "quest": quest,
    #     }
    #     return super().get(request, *args, **kwargs)

    def get_success_url(self):
        date_value = self.request.POST.get("date")

        base_url = reverse("dairyapp:quest_list")

        query_string = urlencode({'date': date_value})

        return f"{base_url}?{query_string}"


class DayUpdateView(UpdateView):
    model = Day
    fields = "content",
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("dairyapp:quest_list")
    context_object_name = "day"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["day"] = Day.objects.select_related("origin").get(pk=context["pk"])
    #     return context

    def get_success_url(self):
        date_value = self.request.POST.get("date")

        base_url = reverse("dairyapp:quest_list")

        query_string = urlencode({'date': date_value})

        return f"{base_url}?{query_string}"


class OriginDeleteView(DeleteView):
    model = Origin
    success_url = reverse_lazy("dairyapp:origin_list")


class QuestDeleteView(DeleteView):
    model = Quest

    def get_success_url(self):
        date_value = self.request.POST.get("date")

        base_url = reverse("dairyapp:quest_list")

        query_string = urlencode({'date': date_value})

        return f"{base_url}?{query_string}"
