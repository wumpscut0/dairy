from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import OriginListView, OriginUpdateView, IndexTemplateView, OriginCreateView, QuestListView, QuestFormView, \
    QuestUpdateView, OriginDeleteView, QuestDeleteView

app_name = "dairyapp"


urlpatterns = [
    path("", view=IndexTemplateView.as_view(), name="index"),
    path("origin", view=OriginListView.as_view(), name="origin_list"),
    path("origin/<int:pk>/update", view=OriginUpdateView.as_view(), name="origin_update"),
    path("origin/form", view=OriginCreateView.as_view(), name="origin_form"),
    path("origin/<int:pk>/delete", view=OriginDeleteView.as_view(), name="origin_delete"),
    path("quest/", view=QuestListView.as_view(), name="quest_list"),
    path("quest/accept", view=QuestFormView.as_view(), name="quest_form"),
    path("quest/<int:pk>/update", view=QuestUpdateView.as_view(), name="quest_update_form"),
    path("quest/<int:pk>/delete", view=QuestDeleteView.as_view(), name="quest_delete"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


