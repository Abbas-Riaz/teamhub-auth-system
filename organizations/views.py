from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
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

    def get(self, request, pk):
        organization = get_object_or_404(
            Organization.objects.filter(members=request.user).select_related("owner"),
            pk=pk,
        )
        serializer = OrganizationSerializer(organization, context={"request": request})
        return Response(serializer.data)
