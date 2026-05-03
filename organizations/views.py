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
