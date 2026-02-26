from django.urls import path
from .views import OrganizationListView

urlpatterns = [
    path("", OrganizationListView.as_view(), name="organizations"),
]
