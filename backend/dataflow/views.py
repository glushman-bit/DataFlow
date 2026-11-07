from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from dataflow.models import DataTable, DataField
from dataflow.serializers import DataTableSerializer, DataFieldSerializer


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


class DataFieldViewSet(viewsets.ModelViewSet):
    """API для управления полями пользовательских таблиц."""

    serializer_class = DataFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает поля только таблицы текущего пользователя."""
        return DataField.objects.filter(
            table_id=self.kwargs['table_id'],
            table__owner=self.request.user
        )

    def perform_create(self, serializer):
        """Создаёт поле в таблице текущего пользователя."""
        table = get_object_or_404(
            DataTable,
            pk=self.kwargs['table_id'],
            owner=self.request.user
        )

        serializer.save(table=table)
