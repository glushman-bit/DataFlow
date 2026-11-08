from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from dataflow.models import DataTable, DataField, DataRecord
from dataflow.serializers import (
    DataTableSerializer,
    DataFieldSerializer,
    DataRecordSerializer,
)


class DataTableViewSet(viewsets.ModelViewSet):
    """API для управления пользовательскими таблицами."""

    serializer_class = DataTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только таблицы текущего пользователя."""
        # get_queryset() ограничивает доступ к записям конкретной таблицей и её владельцем.

        if getattr(self, "swagger_fake_view", False):
            return DataField.objects.none()

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

        if getattr(self, "swagger_fake_view", False):
            return DataField.objects.none()

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


class DataRecordViewSet(viewsets.ModelViewSet):
    """API для управления записями пользовательских таблиц."""

    serializer_class = DataRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает записи только таблицы текущего пользователя."""

        if getattr(self, "swagger_fake_view", False):
            return DataField.objects.none()

        return DataRecord.objects.filter(
            table_id=self.kwargs['table_id'],
            table__owner=self.request.user,
        )

    def get_serializer_context(self):
        """Передаёт таблицу и HTTP-запрос в сериализатор."""
        context = super().get_serializer_context()  # get_serializer_context() передаёт сериализатору таблицу, чтобы тот мог проверить значения относительно её полей.
                                                    # request уже автоматически передаётся стандартным методом DRF get_serializer_context().

        if getattr(self, "swagger_fake_view", False):
            return context

        context["table"] = get_object_or_404(
            DataTable,
            pk=self.kwargs['table_id'],
            owner=self.request.user
        )

        return context
