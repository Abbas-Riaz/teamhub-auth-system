from rest_framework import serializers
from .models import Organization, OrganizationMembership, Invitation
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for organization details
    Used in: GET /api/organizations/, GET /api/organizations/{id}/
    """

    # Include owner's email (follow relationship)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    # Calculate member count dynamically
    member_count = serializers.SerializerMethodField()

    # Show current user's role in this org
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "owner",
            "owner_email",
            "member_count",
            "user_role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj):
        """Return total members in organization"""
        return obj.members.count()

    def get_user_role(self, obj):
        """Return current user's role in this organization"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                membership = OrganizationMembership.objects.get(
                    organization=obj, user=request.user
                )
                return membership.role
            except OrganizationMembership.DoesNotExist:
                return None
        return None


class CreateOrganizationSerializer(serializers.ModelSerializer):
    """
    Create organization serializer
    Used in: POST /api/organizations/
    Auto-sets owner to current user
    """

    class Meta:
        model = Organization
        fields = ["name", "description"]

    def create(self, validated_data):
        """
        Override create to:
        1. Set owner to current user
        2. Create organization
        3. Auto-create membership with 'owner' role
        """
        request = self.context.get("request")
        user = request.user

        # Create organization
        organization = Organization.objects.create(
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            owner=user,
        )

        # Auto-create membership for owner
        OrganizationMembership.objects.create(
            organization=organization, user=user, role="owner"
        )

        return organization

    def validate_name(self, value):
        """Ensure organization name is unique for this user"""
        request = self.context.get("request")
        if Organization.objects.filter(name__iexact=value, owner=request.user).exists():
            raise serializers.ValidationError(
                "You already have an organization with this name."
            )
        return value


class CreateOrganizationSerializer(serializers.ModelSerializer):
    """
    Create organization
    - Auto-sets owner to current user
    - Auto-creates membership with role='owner'
    """

    class Meta:
        model = Organization
        fields = ["name", "description"]  # Only what user provides

    def create(self, validated_data):
        # Get user from context
        request = self.context.get("request")
        user = request.user

        # Create organization
        organization = Organization.objects.create(
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            owner=user,
        )

        # Create membership
        OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role="owner",
        )

        return organization

    def validate_name(self, value):
        request = self.context.get("request")

        if Organization.objects.filter(name__iexact=value, owner=request.user).exists():
            raise serializers.ValidationError(
                "You already have an organization with this name."
            )

        return value
