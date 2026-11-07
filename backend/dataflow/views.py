from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from dataflow.models import DataTable
from dataflow.serializers import DataTableSerializer


class DataTableViewSet(viewsets.ModelViewSet):
    """API для управления пользовательскими таблицами."""

    serializer_class = DataTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только таблицы текущего пользователя."""
        return DataTable.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """При создании автоматически назначает владельца."""
        serializer.save(owner=self.request.user)
