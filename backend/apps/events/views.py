from rest_framework import viewsets, permissions
from .models import Conference
from .serializers import ConferenceSerializer
from django.shortcuts import render

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

class ConferenceViewSet(viewsets.ModelViewSet):
    queryset = Conference.objects.all()
    serializer_class = ConferenceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['location', 'start_date']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

def conference_list(request):
    conferences = Conference.objects.all()
    return render(request, 'conference_list.html', {'conferences': conferences})