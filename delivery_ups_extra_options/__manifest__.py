# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    'name': "Delivery UPS Extra Options",
    'summary': """This module is used to send the extra information to UPS""",
    'version': '15.0.1.0.0',
    'category': 'Generic Modules/Others',
    'website': "http://sodexis.com/",
    'author': "Sodexis",
    'license': 'OEEL-1',
    'installable': True,
    'depends': [
        'sale',
        'delivery_ups',
        'delivery_base_extra_options',
        'sale_ship_term',
        'stock',
    ],
    'data': [
        'wizard/choose_delivery_package_view.xml',
        'views/res_config_settings.xml',
        'views/res_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/sale_view.xml',
        'views/stock_package_type.xml',
        'views/stock_picking_view.xml',
        'views/stock_quant_package_view.xml',
    ],
}