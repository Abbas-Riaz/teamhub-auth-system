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


"""======================== organization invite members serialzers============================="""

from rest_framework import serializers
from .models import Invitation, OrganizationMembership
from django.utils import timezone
from datetime import timedelta
from django.core import signing


class InviteUserSerializer(serializers.Serializer):
    """
    Serializer for inviting users to organization
    Used in: POST /api/organizations/{id}/invite/

    Owner/Admin sends email to invite new member
    """

    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(
        choices=["admin", "member", "viewer"], default="member"  # Can't invite as owner
    )

    def validate_email(self, value):
        """
        Check if user already member or already invited
        """
        # Get organization from context (passed from view)
        organization = self.context.get("organization")

        # Check if user with this email is already a member
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(email=value)
            # User exists - check if already member
            if OrganizationMembership.objects.filter(
                organization=organization, user=user
            ).exists():
                raise serializers.ValidationError(
                    "User is already a member of this organization."
                )
        except User.DoesNotExist:
            # User doesn't exist yet - that's fine, can still invite
            pass

        # Check if already has pending invitation
        if Invitation.objects.filter(
            organization=organization, email=value, status="pending"
        ).exists():
            raise serializers.ValidationError(
                "An invitation has already been sent to this email."
            )

        return value

    def create(self, validated_data):
        """
        Create invitation with secure token
        """
        organization = self.context.get("organization")
        invited_by = self.context.get("invited_by")

        # Generate secure token
        token_data = {
            "email": validated_data["email"],
            "org_id": str(organization.id),
            "timestamp": timezone.now().timestamp(),
        }
        token = signing.dumps(token_data, salt="invitation")

        # Create invitation
        invitation = Invitation.objects.create(
            organization=organization,
            email=validated_data["email"],
            role=validated_data["role"],
            invited_by=invited_by,
            token=token,
            status="pending",
            expires_at=timezone.now() + timedelta(days=7),  # 7 days expiry
        )

        return invitation


class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying invitation details
    Used in: GET /api/invitations/ (list user's pending invites)
    """

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "organization",
            "organization_name",
            "email",
            "role",
            "invited_by",
            "invited_by_email",
            "status",
            "created_at",
            "expires_at",
            "is_expired",
        ]
        read_only_fields = ["id", "status", "created_at", "expires_at"]

    def get_is_expired(self, obj):
        """Check if invitation has expired"""
        return obj.is_expired()


class AcceptInvitationSerializer(serializers.Serializer):
    """
    Serializer for accepting invitation
    Used in: POST /api/invitations/{id}/accept/

    Validates token and creates membership
    """

    def validate(self, data):
        """
        Validate invitation can be accepted
        """
        invitation = self.context.get("invitation")
        user = self.context.get("user")

        # Check if expired
        if invitation.is_expired():
            raise serializers.ValidationError({"error": "This invitation has expired."})

        # Check if already used
        if invitation.status != "pending":
            raise serializers.ValidationError(
                {"error": f"This invitation has already been {invitation.status}."}
            )

        # Check email matches
        if user.email != invitation.email:
            raise serializers.ValidationError(
                {"error": "This invitation was sent to a different email address."}
            )

        # Check if user already member
        if OrganizationMembership.objects.filter(
            organization=invitation.organization, user=user
        ).exists():
            raise serializers.ValidationError(
                {"error": "You are already a member of this organization."}
            )

        return data

    def save(self):
        """
        Accept invitation: Create membership and update status
        """
        invitation = self.context.get("invitation")
        user = self.context.get("user")

        # Create organization membership
        membership = OrganizationMembership.objects.create(
            organization=invitation.organization, user=user, role=invitation.role
        )

        # Update invitation status
        invitation.status = "accepted"
        invitation.save()

        return membership
