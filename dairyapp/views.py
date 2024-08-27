from datetime import timedelta, datetime
from logging import getLogger

from django.conf import settings
from django.http import HttpRequest, Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView,
    UpdateView,
    DeleteView,
)
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Quest, Origin, Day, TYPES
from .serializers import QuestEditModelSerializer, QuestCreateModelSerializer

logger = getLogger("stdout")


class QuestApi(APIView):
    def get_object(self, pk):
        try:
            return Quest.objects.get(pk=pk)
        except Quest.DoesNotExist:
            raise Http404

    def post(self, request: Request):
        serializer = QuestCreateModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.debug(f"POST(REST) validator errors {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request, pk: int):
        serializer = QuestEditModelSerializer(self.get_object(pk))
        response = Response(data=serializer.data)
        return response

    def put(self, request: Request, pk: int):
        logger.debug(f"PUT(REST) request data {request.data}")
        serializer = QuestEditModelSerializer(self.get_object(pk), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        logger.debug(f"PUT(REST) validator errors {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_types(request: Request):
    return JsonResponse(data=TYPES)


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


class QuestCreateTemplateView(TemplateView):
    template_name = "dairyapp/quest_form.html"
    
    def get(self, request, *args, **kwargs):
        default_origin = self._extract_actual_origin()
        if default_origin is None:
            return redirect(reverse("dairyapp:origin_list"))
        
        context = self.get_context_data(**kwargs)
        context.update({
                "endpoint": f"http://{settings.API_HOST}:{settings.API_PORT}/api/quest/create",
                "date": self.request.GET.get("date"),
                "origins": Origin.objects.all(),
                "default_origin": default_origin,
                "tasks_types": TYPES["tasks"],
        })
        return self.render_to_response(context)

    @staticmethod
    def _extract_actual_origin():
        new_origin = (
            Origin.objects.filter(status="a", last_extracted_at=None)
            .order_by("created_at")
            .first()
        )
        if new_origin:
            actual_origin = new_origin
        else:
            actual_origin = Origin.objects.filter(status="a").first()
            
        if not actual_origin:
            return Origin.objects.filter(status="f").first()
        return actual_origin


class QuestListView(ListView):
    model = Quest
    context_object_name = "object_list"
    template_name = "dairyapp/quest_list.html"
    delta_day = timedelta(days=1)

    def get_queryset(self):
        date = self.request.GET.get("date", now().date())
        if isinstance(date, str):
            date = datetime.fromisoformat(date).date()
        return (
            Quest.objects.filter(created_at__date=date)
            .select_related("origin")
            .order_by("created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.request.GET.get("date", now().date())
        if isinstance(date, str):
            date = datetime.fromisoformat(date).date()
        day, created = Day.objects.get_or_create(
            created_at__date=date, defaults={"created_at": date}
        )
        context["day"] = day
        context["date"] = date
        context["has_previous"] = Quest.objects.filter(
            created_at__date__lt=date
        ).exists()
        context["has_next"] = date < datetime.now().date()
        return context

    def get(self, request: HttpRequest, *args, **kwargs):
        date_str = request.GET.get("date")
        if date_str:
            date = datetime.fromisoformat(date_str).date()
        else:
            date = now().date()

        if "previous" in request.GET:
            date -= self.delta_day
        elif "next" in request.GET:
            date += self.delta_day

        request.GET = request.GET.copy()
        request.GET["date"] = date.isoformat()

        return super().get(request, *args, **kwargs)


class QuestEditTemplateView(TemplateView):
    template_name = "dairyapp/quest_update_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["quest"] = Quest.objects.get(pk=self.kwargs.get("pk", -1))
            context["endpoint"] = (
                f"http://{settings.API_HOST}:{settings.API_PORT}/api/quest/{context["quest"].pk}/update"
            )
            context["quest_data"] = QuestEditModelSerializer(context["quest"]).data
            return context
        except Quest.DoesNotExist:
            raise Http404


class DayUpdateView(UpdateView):
    model = Day
    fields = ("content",)
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("dairyapp:quest_list")
    context_object_name = "day"

    def get_success_url(self):
        date_value = self.request.POST.get("date")

        base_url = reverse("dairyapp:quest_list")

        query_string = urlencode({"date": date_value})

        return f"{base_url}?{query_string}"


class OriginDeleteView(DeleteView):
    model = Origin
    success_url = reverse_lazy("dairyapp:origin_list")


class QuestDeleteView(DeleteView):
    model = Quest

    def get_success_url(self):
        date_value = self.request.POST.get("date")

        base_url = reverse("dairyapp:quest_list")

        query_string = urlencode({"date": date_value})

        return f"{base_url}?{query_string}"
