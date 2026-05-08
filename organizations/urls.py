from django.urls import path
from .views import (
    OrganizationListView,
    OrganizationDetailView,
    AcceptInvitationView,
    DeclineInvitationView,
    InviteUserView,
    InvitationListView,
)

urlpatterns = [
    path("", OrganizationListView.as_view(), name="organizations"),
    path("<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    # Organization endpoints
    path("", OrganizationListView.as_view(), name="organization-list"),
    path("<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    # Invitation endpoints
    path("<uuid:pk>/invite/", InviteUserView.as_view(), name="invite-user"),
    # User's invitations (not nested under organizations)
    path("invitations/", InvitationListView.as_view(), name="invitation-list"),
    path(
        "invitations/<uuid:pk>/accept/",
        AcceptInvitationView.as_view(),
        name="accept-invitation",
    ),
    path(
        "invitations/<uuid:pk>/decline/",
        DeclineInvitationView.as_view(),
        name="decline-invitation",
    ),
]
