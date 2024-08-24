from django.urls import path

from .views import OriginListView, OriginUpdateView, IndexTemplateView, OriginCreateView, QuestListView, QuestFormView, \
    QuestTemplateView, OriginDeleteView, QuestDeleteView, DayUpdateView, get_types, QuestApi

app_name = "dairyapp"


urlpatterns = [
    path("", view=IndexTemplateView.as_view(), name="index"),
    path("origin", view=OriginListView.as_view(), name="origin_list"),
    path("origin/<int:pk>/update", view=OriginUpdateView.as_view(), name="origin_update"),
    path("origin/create", view=OriginCreateView.as_view(), name="origin_form"),
    path("origin/<int:pk>/delete", view=OriginDeleteView.as_view(), name="origin_delete"),
    path("quest/", view=QuestListView.as_view(), name="quest_list"),
    path("quest/create", view=QuestFormView.as_view(), name="quest_form"),
    path("quest/<int:pk>/update", view=QuestTemplateView.as_view(), name="quest_update_form"),
    path("quest/<int:pk>/delete", view=QuestDeleteView.as_view(), name="quest_delete"),
    path("day/<int:pk>/update", view=DayUpdateView.as_view(), name="day_update_form"),
    path("api/quest/<int:pk>", view=QuestApi.as_view()),
    path("api/meta/types", view=get_types),
]


