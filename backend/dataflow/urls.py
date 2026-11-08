from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from dataflow.views import DataTableViewSet, DataFieldViewSet, DataRecordViewSet

router = DefaultRouter()

router.register("tables", DataTableViewSet, basename="tables")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "tables/<int:table_id>/fields/",
        DataFieldViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="data_fields"),
    path(
        "tables/<int:table_id>/fields/<int:pk>/",
        DataFieldViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy"
        }),
        name="table_field_detail"),
    path(
        "tables/<int:table_id>/records/",
        DataRecordViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="table_records",
    ),
    path(
        "tables/<int:table_id>/records/<int:pk>/",
        DataRecordViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="table_record_detail"
    )
]

urlpatterns += router.urls
