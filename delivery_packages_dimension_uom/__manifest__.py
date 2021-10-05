# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    'name': "Delivery Packages Dimension UOM",
    'summary': """
        This module allows to display the package dimension uom on packages,
        delivery packages and also in choose delivery package wizard.""",
    'version': "14.0.1.0.0",
    'category': 'Delivery Packages',
    'website': "http://sodexis.com/",
    'author': "Sodexis",
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'depends': [
        'delivery',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_packaging_view.xml',
    ],
}
