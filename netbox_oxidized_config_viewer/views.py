import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from dcim.models import Device
from utilities.views import ViewTab, register_model_view
from datetime import datetime, timezone
from json import JSONDecodeError
from .tables import OxidizedConfigViewerTable, BackupDetailListTable
from .utils import generate_unified_diff

# View to expose Oxidized API URL
def oxidized_api_url(request):
    try:
        oxidized_api_url = settings.PLUGINS_CONFIG["netbox_oxidized_config_viewer"]["oxidized_api_url"]
        return JsonResponse({"url": oxidized_api_url})
    except KeyError:
        return JsonResponse({"error": "Oxidized API URL not configured"}, status=500)

@register_model_view(Device, name="config-backup")
class ConfigBackupView(View):
    tab = ViewTab(
        label="Oxidized",
        permission="dcim.view_device",
    )

    def get(self, request, pk):
        device = Device.objects.get(pk=pk)
        config_a = ""
        config_b = ""
        backups = []
        selected_backup_date = None
        selected_backup_id = request.GET.get("backup")
        backup_a_id = request.GET.get("backup_a")
        backup_b_id = request.GET.get("backup_b")
        diff_mode = request.GET.get("diff") == "True"

        try:
            oxidized_api_url = settings.PLUGINS_CONFIG[
                "netbox_oxidized_config_viewer"
            ]["oxidized_api_url"]

            # Try to get list of backups
            try:
                list_url = f"{oxidized_api_url.rstrip('/')}/node/version.json?node_full={device.name}"
                response = requests.get(list_url)
                response.raise_for_status()
                backup_data = response.json()

                if backup_data:
                    backups = sorted(
                        [
                            {
                                "id": v["oid"],
                                "date": datetime.strptime(
                                    v["time"], "%Y-%m-%d %H:%M:%S %z"
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                            }
                            for v in backup_data
                        ],
                        key=lambda x: x["date"],
                        reverse=True,
                    )
            except (requests.exceptions.RequestException, JSONDecodeError) as e:
                messages.warning(
                    request, f"Could not retrieve backup list from Oxidized: {e}"
                )

            if diff_mode and backup_a_id and backup_b_id:
                # Fetch config A
                fetch_url_a = f"{oxidized_api_url.rstrip('/')}/node/version/view.text?node={device.name}&oid={backup_a_id}"
                response_a = requests.get(fetch_url_a)
                response_a.raise_for_status()
                config_a = response_a.text

                # Fetch config B
                fetch_url_b = f"{oxidized_api_url.rstrip('/')}/node/version/view.text?node={device.name}&oid={backup_b_id}"
                response_b = requests.get(fetch_url_b)
                response_b.raise_for_status()
                config_b = response_b.text

                if "export" in request.GET:
                    # For export in diff mode, return both configs separated
                    return HttpResponse(f"--- Config A ---\n{config_a}\n\n--- Config B ---\n{config_b}", content_type="text/plain")

            else:
                # Determine which single config to fetch
                if selected_backup_id:
                    fetch_url = f"{oxidized_api_url.rstrip('/')}/node/version/view.text?node={device.name}&oid={selected_backup_id}"
                    # Find the date for the selected backup
                    for backup in backups:
                        if backup["id"] == selected_backup_id:
                            selected_backup_date = backup["date"]
                            break
                else:
                    fetch_url = f"{oxidized_api_url.rstrip('/')}/node/fetch/{device.name}"
                    if backups:
                        selected_backup_date = backups[0]["date"]
                        selected_backup_id = backups[0]["id"]

                # Fetch the configuration from the Oxidized API
                response = requests.get(fetch_url)
                response.raise_for_status()
                config_a = response.text # Use config_a for single config display

                if "export" in request.GET:
                    return HttpResponse(config_a, content_type="text/plain")

        except requests.exceptions.RequestException as e:
            messages.error(
                request, f"Failed to fetch configuration from Oxidized: {e}"
            )
        except KeyError:
            messages.error(request, "Oxidized API URL not configured.")

        context = {
            "object": device,
            "config": config_a, # This will be used for single view
            "config_a": config_a, # Pass both for diff view
            "config_b": config_b,
            "tab": self.tab,
            "backups": backups,
            "selected_backup_id": selected_backup_id,
            "selected_backup_date": selected_backup_date,
            "diff_mode": diff_mode,
            "backup_a_id": backup_a_id,
            "backup_b_id": backup_b_id,
            "is_diff_mode": diff_mode,  # Add this for the template to use
        }

        # If in diff mode, add the diff string to the context
        if diff_mode and backup_a_id and backup_b_id:
            # Get the dates for the selected backups
            backup_a_date = None
            backup_b_date = None
            for backup in backups:
                if backup["id"] == backup_a_id:
                    backup_a_date = backup["date"]
                if backup["id"] == backup_b_id:
                    backup_b_date = backup["date"]
            
            # Use dates in the diff headers instead of backup IDs
            from_filename = f"Backup {backup_a_date or backup_a_id}"
            to_filename = f"Backup {backup_b_date or backup_b_id}"
            
            context["diff_string"] = generate_unified_diff(
                config_a, config_b, from_filename=from_filename, to_filename=to_filename
            )

        return render(
            request,
            "netbox_oxidized_config_viewer/oxidized-config-viewer.html",
            context=context,
        )

class OxidizedListView(View):
    def get(self, request):
        devices_from_oxidized = []
        try:
            oxidized_api_url = settings.PLUGINS_CONFIG[
                "netbox_oxidized_config_viewer"
            ]["oxidized_api_url"]
            list_url = f"{oxidized_api_url.rstrip('/')}/nodes.json"
            response = requests.get(list_url)
            response.raise_for_status()
            devices_from_oxidized = response.json()

            for device in devices_from_oxidized:
                # Get device name
                device_name = device.get("name")

                # Get last attempted backup time
                last_attempted = device.get("last", {}).get("start")
                # Get last successful backup time
                last_successful = device.get("last", {}).get("end")
                # Get status
                status = device.get("last", {}).get("status", "never")
                # Get last changed time
                last_changed = device.get("mtime")

                # Parse timestamps
                def parse_timestamp(timestamp):
                    if not timestamp:
                        return None
                    parsed = None
                    if isinstance(timestamp, str):
                        try:
                            if timestamp.endswith(" UTC"):
                                naive_dt = datetime.strptime(timestamp.replace(" UTC", ""), "%Y-%m-%d %H:%M:%S")
                                parsed = naive_dt.replace(tzinfo=timezone.utc)
                            elif 'T' in timestamp:
                                if timestamp.endswith('Z'):
                                    timestamp = timestamp[:-1] + '+00:00'
                                parsed = datetime.fromisoformat(timestamp)
                            else:
                                parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z")
                        except ValueError:
                            parsed = None
                    elif isinstance(timestamp, (int, float)):
                        try:
                            parsed = datetime.fromtimestamp(timestamp, timezone.utc)
                        except (ValueError, OSError):
                            parsed = None
                    return parsed

                # Apply parsed timestamps
                device["last_attempted"] = parse_timestamp(last_attempted)
                device["last_successful"] = parse_timestamp(last_successful)
                device["last_changed"] = parse_timestamp(last_changed)
                device["status"] = status

        except requests.exceptions.RequestException as e:
            messages.error(
                request, f"Failed to fetch devices from Oxidized: {e}"
            )
        except KeyError:
            messages.error(request, "Oxidized API URL not configured.")
        except JSONDecodeError as e:
            messages.error(request, f"Failed to parse JSON from Oxidized: {e}")

        # Filter out devices that don't have a name
        devices_from_oxidized = [d for d in devices_from_oxidized if d.get("name")]

        table = OxidizedConfigViewerTable(devices_from_oxidized)
        table.paginate(page=request.GET.get('page', 1), per_page=25)

        return render(
            request,
            "netbox_oxidized_config_viewer/oxidized_list.html",
            {
                "table": table,
            },
        )

class OxidizedRefreshView(View):
    def get(self, request):
        return render(
            request,
            "netbox_oxidized_config_viewer/oxidized_refresh.html",
            {},
        )

    def post(self, request):
        if request.POST.get("confirm") == "yes":
            try:
                oxidized_api_url = settings.PLUGINS_CONFIG[
                    "netbox_oxidized_config_viewer"
                ]["oxidized_api_url"]
                reload_url = f"{oxidized_api_url.rstrip('/')}/reload"
                response = requests.get(reload_url)
                response.raise_for_status()
                messages.success(request, "Successfully triggered node refresh in Oxidized.")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Failed to trigger node refresh in Oxidized: {e}")
            except KeyError:
                messages.error(request, "Oxidized API URL not configured.")
        else:
            messages.info(request, "Node refresh cancelled.")

        return redirect("plugins:netbox_oxidized_config_viewer:oxidized_list")

# New view for handling backup detail list API requests
class BackupDetailListView(View):
    def get(self, request, device_name):
        try:
            oxidized_api_url = settings.PLUGINS_CONFIG[
                "netbox_oxidized_config_viewer"
            ]["oxidized_api_url"]

            # Get list of backups
            list_url = f"{oxidized_api_url.rstrip('/')}/node/version.json?node_full={device_name}"
            response = requests.get(list_url)
            response.raise_for_status()
            backup_data = response.json()

            backups = []
            if backup_data:
                # Per user feedback, the numbering is based on the order in the JSON result.
                # 0 is current, 1 is previous, etc. We assume the API returns them in order.
                for i, v in enumerate(backup_data):
                    backups.append(
                        {
                            "id": v["oid"],
                            "date": datetime.strptime(
                                v["time"], "%Y-%m-%d %H:%M:%S %z"
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "number": i,
                        }
                    )

            table = BackupDetailListTable(backups, device_name=device_name)
            return render(
                request,
                "netbox_oxidized_config_viewer/backup_detail_list.html",
                {"table": table},
            )

        except (requests.exceptions.RequestException, JSONDecodeError) as e:
            return HttpResponse(f"Error: {e}", status=500)
        except KeyError:
            return HttpResponse("Error: Oxidized API URL not configured", status=500)
class DownloadConfigView(View):
    def get(self, request, device_name, backup_id):
        try:
            oxidized_api_url = settings.PLUGINS_CONFIG[
                "netbox_oxidized_config_viewer"
            ]["oxidized_api_url"]
            fetch_url = f"{oxidized_api_url.rstrip('/')}/node/version/view.text?node={device_name}&oid={backup_id}"
            response = requests.get(fetch_url)
            response.raise_for_status()
            config_content = response.text
            
            http_response = HttpResponse(config_content, content_type='text/plain')
            http_response['Content-Disposition'] = f'attachment; filename="{device_name}_{backup_id}.txt"'
            return http_response

        except requests.exceptions.RequestException as e:
            messages.error(
                request, f"Failed to fetch configuration from Oxidized: {e}"
            )
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except KeyError:
            messages.error(request, "Oxidized API URL not configured.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
