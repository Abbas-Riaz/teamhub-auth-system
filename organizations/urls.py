from django.urls import path
from .views import OrganizationListView, OrganizationDetailView

urlpatterns = [
    path("", OrganizationListView.as_view(), name="organizations"),
    path("<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
]
