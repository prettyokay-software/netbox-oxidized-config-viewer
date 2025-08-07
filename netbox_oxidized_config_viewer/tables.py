import django_tables2 as tables
from dcim.models import Device
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import localtime

class OxidizedConfigViewerTable(tables.Table):
    backups = tables.TemplateColumn(
        '<a href="#" class="show-backups" data-device-name="{{ record.name }}"><i class="mdi mdi-chevron-right"></i></a>',
        verbose_name="",
        orderable=False
    )
    name = tables.Column(attrs={"td": {"class": "link-column"}}, verbose_name="Device Name")
    last_changed = tables.Column(verbose_name="Last Changed", accessor="last_changed")
    last_backup = tables.Column(verbose_name="Last Backup", accessor="last_successful")
    status = tables.Column(verbose_name="Status")


    def render_name(self, value, record):
        # Find the corresponding NetBox device by name and get its primary key
        try:
            device = Device.objects.get(name=record["name"])
            return mark_safe(f'<a href="/dcim/devices/{device.pk}/">{record["name"]}</a>')
        except Device.DoesNotExist:
            return record["name"]

    def render_last_changed(self, value, record):
        if value:
            local_time = localtime(value)
            formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
            return format_html('<span title="{}">{}</span>',
                               local_time, formatted_time)
        return "-"

    def render_last_backup(self, value, record):
        if value:
            local_time = localtime(value)
            formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
            # Find the corresponding NetBox device by name and create a hyperlink to the config-backup tab
            try:
                device = Device.objects.get(name=record["name"])
                url = f"/dcim/devices/{device.pk}/config-backup/"
                return format_html('<a href="{}">{}</a>',
                                  url, formatted_time)
            except Device.DoesNotExist:
                return format_html('<span title="{}">{}</span>',
                                local_time, formatted_time)
        return "-"

    def render_status(self, value, record):
        if value == "success":
            return format_html('<span class="badge bg-success text-body">Success</span>')
        elif value == "failed":
            return format_html('<span class="badge bg-danger text-body">Failed</span>')
        elif value == "never":
            return format_html('<span class="badge bg-secondary text-body">Never</span>')
        return value

    class Meta:
        fields = ("backups", "name", "last_changed", "last_backup", "status")
        default_columns = ("backups", "name", "last_changed", "last_backup", "status")
        order_by = "name"
        attrs = {"class": "table table-hover table-responsive"}
        row_attrs = {
            "data-name": lambda record: record["name"],
            "data-status": lambda record: record.get("status", ""),
        }

class BackupDetailListTable(tables.Table):
    download = tables.TemplateColumn(
        template_code='<a href="{% url \'plugins:netbox_oxidized_config_viewer:download_config\' device_name=table.device_name backup_id=record.id %}" target="_blank"><i class="mdi mdi-download"></i></a>',
        verbose_name="",
        attrs={"th": {"style": "width:2%; white-space:nowrap"}, "td": {"class": "text-center"}},
        orderable=False
    )
    number = tables.Column(verbose_name="Version", attrs={"th": {"style": "width:2%; white-space:nowrap"}, "td": {"class": "text-center"}})
    date = tables.Column(verbose_name="Date Saved")

    def __init__(self, *args, device_name=None, **kwargs):
        self.device_name = device_name
        super().__init__(*args, **kwargs)

    def render_number(self, value, record):
        try:
            device = Device.objects.get(name=self.device_name)
            url = f"/dcim/devices/{device.pk}/config-backup/?backup={record['id']}"
            return format_html('<a href="{}">{}</a>', url, value)
        except Device.DoesNotExist:
            return value

    class Meta:
        fields = ("download", "number", "date")
        order_by = "number"
        attrs = {"class": "table table-hover table-responsive table-sm"}
