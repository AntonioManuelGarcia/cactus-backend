from rest_framework import generics, permissions
from .models import Task
from .serializers import TaskSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=TaskSerializer,
    responses=TaskSerializer(many=True),
    description="Lista y crea tareas del usuario autenticado"
)
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(
    request=TaskSerializer,
    responses=TaskSerializer,
    description="Obtiene, actualiza o elimina una tarea propia"
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
