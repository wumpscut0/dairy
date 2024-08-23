from datetime import timedelta, datetime
from json import load
from pathlib import Path

from django.http import HttpRequest, Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Quest, Origin, Day
from .serializers import QuestModelSerializer


class QuestApi(APIView):
    def get_object(self, pk):
        try:
            return Quest.objects.get(pk=pk)
        except Quest.DoesNotExist:
            raise Http404

    def get(self, request: Request, pk: int):
        serializer = QuestModelSerializer(self.get_object(pk))
        response = Response(data=serializer.data)
        return response

    def put(self, request: Request, pk: int):
        print("put", request.data)
        serializer = QuestModelSerializer(self.get_object(pk), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_error_types(request: Request):
    with open(Path("errors_types.json").resolve()) as file:
        return JsonResponse(data=load(file))


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
            date = datetime.fromisoformat(date).date()
        return Quest.objects.filter(created_at__date=date).select_related("origin").order_by("created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get('date', now().date())
        if isinstance(date, str):
            date = datetime.fromisoformat(date).date()
        day, created = Day.objects.get_or_create(created_at__date=date, defaults={"created_at": date})
        context['day'] = day
        context['date'] = date
        context['has_previous'] = Quest.objects.filter(created_at__date__lt=date).exists()
        context['has_next'] = not not (Quest.objects.filter(created_at__date__gt=date).exists() or date.day == now().day - 1)
        return context

    def get(self, request: HttpRequest, *args, **kwargs):
        date_str = request.GET.get('date')
        if date_str:
            date = datetime.fromisoformat(date_str).date()
        else:
            date = now().date()

        if 'previous' in request.GET:
            date -= self.delta_day
        elif 'next' in request.GET:
            date += self.delta_day

        request.GET = request.GET.copy()
        request.GET['date'] = date.isoformat()

        return super().get(request, *args, **kwargs)


class QuestTemplateView(TemplateView):
    template_name = "dairyapp/quest_update_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["quest"] = Quest.objects.get(pk=self.kwargs.get("pk", -1))
        except Quest.DoesNotExist:
            raise Http404
        return context

class DayUpdateView(UpdateView):
    model = Day
    fields = "content",
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("dairyapp:quest_list")
    context_object_name = "day"

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
