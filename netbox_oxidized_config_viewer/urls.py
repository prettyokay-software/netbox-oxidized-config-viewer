from django.urls import path
from .views import (
    ConfigBackupView,
    OxidizedListView,
    OxidizedRefreshView,
    oxidized_api_url,
    BackupDetailListView,
    DownloadConfigView,
)

urlpatterns = [
    path("list/", OxidizedListView.as_view(), name="oxidized_list"),
    path("refresh/", OxidizedRefreshView.as_view(), name="oxidized_refresh"),
    path(
        "api/backup-detail/<str:device_name>/",
        BackupDetailListView.as_view(),
        name="backup_detail_list",
    ),
    path(
        "download/<str:device_name>/<str:backup_id>/",
        DownloadConfigView.as_view(),
        name="download_config",
    ),
]
