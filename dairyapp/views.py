
from datetime import timedelta, datetime

from django.http import HttpRequest
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
        context['has_next'] = Quest.objects.filter(created_at__date__gt=date).exists()
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

error_types = {
        # Ошибки восприятия и внимания
        "inattention": "Недостаток внимания или концентрации, приводящий к пропуску важных деталей.",
        "perception": "Ошибки восприятия данных или сигналов, неправильная интерпретация окружающей среды.",
        "observation": "Недостаточные или неправильные наблюдения, что приводит к искажению фактов.",
        "over_focus": "Слишком узкая фокусировка на одном аспекте задачи, игнорирование других важных деталей.",
        "distraction": "Отвлеченность на несущественные детали, мешающая сосредоточиться на задаче.",

        # Ошибки мышления и логики
        "logic": "Логические ошибки, нарушения в структуре аргументов или выводов.",
        "assumption": "Ошибки, вызванные неверными предположениями или допущениями.",
        "cognitive_bias": "Когнитивные искажения, такие как предвзятость или стереотипное мышление.",
        "heuristic": "Ошибки, вызванные использованием упрощенных методов (эвристик) для решения задачи.",
        "over_generalization": "Ошибки обобщения на основе ограниченного количества примеров.",
        "paradox": "Ошибки, связанные с противоречиями или парадоксами в мышлении.",

        # Ошибки памяти и знаний
        "memory": "Проблемы с запоминанием или воспроизведением информации, ведущие к ошибкам.",
        "knowledge_gap": "Недостаток знаний или навыков, приводящий к неправильным решениям.",
        "false_memory": "Ошибки, связанные с ложными воспоминаниями, искажением фактов.",

        # Ошибки интерпретации и понимания
        "interpretation": "Ошибки в толковании данных или информации, ведущие к неверным выводам.",
        "miscommunication": "Недоразумения, вызванные неправильной передачей или пониманием информации.",
        "ambiguity": "Двойственное понимание из-за неясности или многозначности информации.",

        # Ошибки вычислений и оценок
        "arithmetic": "Ошибки в математических вычислениях, неверные результаты арифметических операций.",
        "calculation": "Ошибки в процессе расчета, не только математического, но и логического.",
        "estimation": "Ошибки при оценке величин или времени, неверные предположения о размерах, объемах и т. д.",
        "approximation": "Ошибки, вызванные упрощением или приблизительными расчетами, которые не учитывают все факторы.",

        # Ошибки планирования и стратегии
        "planning": "Ошибки на этапе планирования, выбор неверной стратегии для выполнения задачи.",
        "optimization": "Ошибки, вызванные неэффективной оптимизацией процессов или ресурсов.",
        "time_management": "Ошибки в управлении временем, пропуск дедлайнов или нерациональное распределение времени.",
        "resource_allocation": "Ошибки в распределении ресурсов, таких как время, деньги, материалы.",

        # Ошибки выполнения и действий
        "execution": "Ошибки при выполнении действий, отклонение от плана или недостаточная точность.",
        "coordination": "Проблемы в координации действий или сотрудничестве с другими людьми.",
        "technical": "Ошибки, связанные с неисправностями техники или неправильным использованием инструментов.",
        "manual": "Ошибки, связанные с физическим выполнением задачи, такие как неправильное движение или манипуляция.",

        # Ошибки суждений и принятия решений
        "judgment": "Неправильная оценка ситуации или факторов, влияющих на принятие решений.",
        "overconfidence": "Излишняя уверенность в своих силах или знаниях, приводящая к риску или ошибкам.",
        "underestimation": "Недооценка сложности задачи или факторов риска, ведущая к неудачам.",
        "decision-making": "Ошибки в процессе принятия решений, выбор неверных альтернатив.",
        "risk_assessment": "Ошибки в оценке рисков, приводящие к неоправданным решениям.",
        "ethical": "Ошибки, связанные с нарушением моральных или этических норм, приводящие к конфликтам или негативным последствиям.",

        # Ошибки взаимодействия с окружающей средой
        "contextual": "Ошибки, вызванные неправильным учетом контекста или условий задачи.",
        "environmental": "Ошибки, вызванные внешними условиями, такими как погода, шум, освещение.",
        "cultural": "Ошибки, связанные с неправильным пониманием или учетом культурных различий.",

        # Ошибки мотивации и эмоций
        "motivation": "Ошибки, вызванные недостатком или избытком мотивации, что может повлиять на качество выполнения задачи.",
        "emotional": "Ошибки, вызванные эмоциональными состояниями, такими как стресс, страх, гнев, влияющие на объективность и рациональность.",

        # Ошибки обучения и адаптации
        "learning": "Ошибки в процессе обучения или применения новых знаний, трудности с усвоением информации.",
        "adaptation": "Ошибки в адаптации к новым условиям или изменениям, неспособность быстро приспособиться.",

        # Системные и организационные ошибки
        "systematic": "Систематические ошибки, повторяющиеся из-за структурных проблем или недостатков в процессе.",
        "procedural": "Ошибки, связанные с нарушением процедур или правил, ведут к отклонению от стандарта.",
        "compliance": "Несоблюдение стандартов, требований или правил, приводящее к ошибкам или санкциям.",
        "bureaucratic": "Ошибки, вызванные чрезмерной бюрократией, затягиванием процессов или препятствиями.",
        "review": "Ошибки на этапе проверки или оценки выполненной работы, недосмотр или пропуск важных аспектов.",

        # Ошибки взаимодействия с другими людьми
        "communication": "Ошибки в передаче или интерпретации информации между людьми, ведут к недопониманию.",
        "conflict": "Ошибки, вызванные межличностными конфликтами, влияющие на выполнение задач.",
        "negotiation": "Ошибки в процессе переговоров, приводящие к неудовлетворительным результатам.",
        "trust": "Ошибки, связанные с неправильным уровнем доверия, как избыточным, так и недостаточным.",
        "collaboration": "Ошибки в совместной работе, вызванные недостаточной координацией или взаимодействием.",

        # Специфические ошибки, связанные с задачей
        "domain_specific": "Ошибки, характерные для конкретной области знаний или специфических задач.",
        "specialization": "Ошибки, вызванные узкой специализацией или недостатком знаний в смежных областях.",
        "tools_usage": "Ошибки в использовании инструментов или технологий, неправильное применение или настройка.",

        # Прочие ошибки
        "random": "Ошибки, которые трудно предсказать или классифицировать, случайные ошибки.",
        "unforeseen": "Ошибки, связанные с неожиданными обстоятельствами или событиями, которые невозможно было предугадать.",
        "external": "Ошибки, вызванные внешними факторами, которые невозможно контролировать.",
        "neglect": "Пренебрежение важными аспектами задачи, ведущее к пропуску или упущению критической информации.",
        "fatigue": "Ошибки, вызванные усталостью или истощением, влияющие на способность концентрироваться и принимать правильные решения."
}

class QuestUpdateView(UpdateView):
    model = Quest
    fields = "theme_description", "total_tasks", "total_completed_tasks", "complete_description", "knowledge"
    template_name_suffix = "_update_form"
    context_object_name = "quest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["options"] = error_types
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        types = [value for name, value in self.request.POST.items() if name.startswith("error_type")]
        descriptions = [value for name, value in self.request.POST.items() if name.startswith("error_description")]
        self.object.errors = [{"type": types[i], "description": descriptions[i]} for i in range(len(types))]
        self.object.last_update = now()
        self.object.save()
        return response

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
