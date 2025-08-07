# Netbox Oxidized Config Viewer

View configurations backed up in Oxidized in Netbox

This project was created using human directed AI coding, primarily Devstral and Google Gemini. 


## To install in its current form

* Download repo and transfer to somewhere close to your Netbox install
* Activate Netbox venv
* `pip install -e path/to/netbox-oxidized-config-viewer`
* Add to Netbox configuration.yml
    * `PLUGINS = [ "netbox_oxidized_config_viewer"]`
    * `PLUGINS_CONFIG = {
    'netbox_oxidized_config_viewer': {
      'oxidized_api_url': 'http://localhost:8888/'
   },`


* Free software: GPL v3
* Documentation: https://.github.io/netbox-oxidized-config-viewer/


## Features
Allows viewing of config from device tab

<img width="1603" height="513" alt="Screenshot 2025-08-07 161609" src="https://github.com/user-attachments/assets/b5facca6-d7b0-4cc0-b93b-417f4507d81c" />

Download previous config versions

Display diff of config versions (alpha version feature)

Lists all devices with config backups as well as their versions

Allows triggering a new backup from Netbox UI

<img width="1862" height="606" alt="Screenshot 2025-08-07 161645" src="https://github.com/user-attachments/assets/af0b2320-f2b5-41ec-a011-a13f50dff74c" />

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.0        |      0.1.0     |

## Installing

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

While this is still in development and not yet on pypi you can install with pip:

```bash
pip install git+https://github.com//netbox-oxidized-config-viewer
```

or by adding to your `local_requirements.txt` or `plugin_requirements.txt` (netbox-docker):

```bash
git+https://github.com//netbox-oxidized-config-viewer
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`,
 or if you use netbox-docker, your `/configuration/plugins.py` file :

```python
PLUGINS = [
    'netbox-oxidized-config-viewer'
]

PLUGINS_CONFIG = {
    "netbox-oxidized-config-viewer": {},
}
```

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.


