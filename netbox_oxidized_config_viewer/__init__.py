"""Top-level package for Netbox Oxidized Config Viewer."""

__author__ = """Adam Cunningham"""
__email__ = "nobody@nobody.com"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class OxidizedConfigViewerConfig(PluginConfig):
    name = "netbox_oxidized_config_viewer"
    verbose_name = "Netbox Oxidized Config Viewer"
    description = "View configurations backed up in Oxidized in Netbox"
    version = __version__
    base_url = "netbox_oxidized_config_viewer"
    required_settings = ["oxidized_api_url"]
    default_settings = {
        "oxidized_api_url": "http://localhost:8888"
    }
    menu = "navigation.menu"


config = OxidizedConfigViewerConfig
