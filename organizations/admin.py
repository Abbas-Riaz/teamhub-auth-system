from django.contrib import admin
from .models import Organization, OrganizationMembership, Invitation


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "created_at"]
    search_fields = ["name", "slug", "owner__email"]
    readonly_fields = ["id", "slug", "created_at", "updated_at"]
    list_filter = ["created_at"]


@admin.register(OrganizationMembership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    search_fields = ["user__email", "organization__name"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "organization",
        "role",
        "status",
        "created_at",
        "expires_at",
    ]
    list_filter = ["status", "role", "created_at"]
    search_fields = ["email", "organization__name"]
    readonly_fields = ["token", "created_at"]
