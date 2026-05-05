from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Organization
from .serializers import OrganizationSerializer, CreateOrganizationSerializer
from rest_framework import status


class OrganizationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter: Only orgs where user is member
        organizations = Organization.objects.filter(members=request.user)

        # Serialize
        serializer = OrganizationSerializer(
            organizations, many=True, context={"request": request}
        )

        # Return
        return Response(serializer.data)

    def post(self, request):
        # Step 1: Validate input with CreateOrganizationSerializer
        serializer = CreateOrganizationSerializer(
            data=request.data, context={"request": request}  # Pass request for context
        )

        # Step 2: Check if valid
        if serializer.is_valid():
            # Step 3: Save (calls our custom create method)
            organization = serializer.save()

            # Step 4: Return full data with OrganizationSerializer
            response_serializer = OrganizationSerializer(
                organization, context={"request": request}
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,  # What status code for creation?
            )

        # Step 5: Return errors if invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """Update organization (owner only)"""
        organization = self.get_object(pk, request.user)

        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is owner
        if organization.owner != request.user:
            return Response(
                {"error": "Only owner can update organization"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update fields
        organization.name = request.data.get("name", organization.name)
        organization.description = request.data.get(
            "description", organization.description
        )
        organization.save()

        # Return updated data
        serializer = OrganizationSerializer(organization, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, pk, user):
        """
        Get organization if user is member
        Returns: Organization object or None
        """
        try:
            return Organization.objects.get(id=pk, members=user)

        except Organization.DoesNotExist:
            return None

    def get(self, request, pk):  # ← ADD THIS METHOD
        """Get single organization details"""
        organization = self.get_object(pk, request.user)

        if not organization:
            return Response(
                {"error": "Organization not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationSerializer(organization, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete organization (owner only)"""
        organization = self.get_object(pk, request.user)

        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if user is owner
        if organization.owner != request.user:
            return Response(
                {"error": "Only owner can delete organization"},
                status=status.HTTP_403_FORBIDDEN,
            )

        organization.delete()

        return Response(
            {"message": "Organization deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


"""========   VIEWS FOR HANDLING INVITATION AND JOINING OF MEMBERS IN ORG """


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Organization, Invitation, OrganizationMembership
from .serializers import (
    InviteUserSerializer,
    InvitationSerializer,
    AcceptInvitationSerializer,
    OrganizationSerializer,
)
from django.shortcuts import get_object_or_404
from .tasks import send_invitation_email


class InviteUserView(APIView):
    """
    Invite user to organization
    POST /api/organizations/{id}/invite/

    Only owner and admins can invite
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Get organization - user must be member
        organization = get_object_or_404(Organization, pk=pk, members=request.user)

        # Check if user is owner or admin (only they can invite)
        try:
            membership = OrganizationMembership.objects.get(
                organization=organization, user=request.user
            )

            if membership.role not in ["owner", "admin"]:
                return Response(
                    {"error": "Only owners and admins can invite users."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except OrganizationMembership.DoesNotExist:
            return Response(
                {"error": "You are not a member of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate and create invitation
        serializer = InviteUserSerializer(
            data=request.data,
            context={"organization": organization, "invited_by": request.user},
        )

        if serializer.is_valid():
            invitation = serializer.save()

            # Send invitation email asynchronously

            send_invitation_email.delay(str(invitation.id))
            # send_invitation_email.delay(invitation.id)

            return Response(
                {
                    "message": f"Invitation sent to {invitation.email}",
                    "invitation": InvitationSerializer(invitation).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvitationListView(APIView):
    """
    List current user's pending invitations
    GET /api/invitations/

    Shows all invites sent to user's email
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get all pending invitations for user's email like user have how many pending request
        invitations = Invitation.objects.filter(
            email=request.user.email, status="pending"
        ).select_related(
            "organization", "invited_by"
        )  # Optimize queries by using select related

        serializer = InvitationSerializer(invitations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptInvitationView(APIView):
    """
    Accept invitation to join organization
    POST /api/invitations/{id}/accept/

    Creates membership and updates invitation status
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Get invitation
        invitation = get_object_or_404(Invitation, pk=pk)

        # Validate and accept
        serializer = AcceptInvitationSerializer(
            data={}, context={"invitation": invitation, "user": request.user}
        )

        if serializer.is_valid():
            membership = serializer.save()

            # Return organization details
            org_serializer = OrganizationSerializer(
                invitation.organization, context={"request": request}
            )

            return Response(
                {
                    "message": f"Successfully joined {invitation.organization.name}",
                    "organization": org_serializer.data,
                    "role": membership.role,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeclineInvitationView(APIView):
    """
    Decline invitation
    POST /api/invitations/{id}/decline/

    Updates invitation status to 'declined'
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Get invitation
        invitation = get_object_or_404(Invitation, pk=pk)

        # Check email matches
        if invitation.email != request.user.email:
            return Response(
                {"error": "This invitation was not sent to you."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if already processed
        if invitation.status != "pending":
            return Response(
                {"error": f"This invitation has already been {invitation.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update status
        invitation.status = "declined"
        invitation.save()

        return Response(
            {"message": "Invitation declined successfully."}, status=status.HTTP_200_OK
        )
