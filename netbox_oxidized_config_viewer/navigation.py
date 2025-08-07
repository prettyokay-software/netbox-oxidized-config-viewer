from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label='Oxidized',
    icon_class='mdi mdi-file-document-outline',
    groups=(
        ('Oxidized', (
            PluginMenuItem(
                link='plugins:netbox_oxidized_config_viewer:oxidized_list',
                link_text='Device List'
            ),
            PluginMenuItem(
                link='plugins:netbox_oxidized_config_viewer:oxidized_refresh',
                link_text='Refresh Nodes'
            ),
        )),
    )
)
