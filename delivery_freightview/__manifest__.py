# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
{
    'name': "FreightView Shipping",
    'summary': "This module offers to send your shippings through FreightView",
    'category': 'Operations/Inventory/Delivery',
    'author': "Sodexis",
    'website': "http://sodexis.com/",
    'version': '15.0.1.0.0',
    'application': True,
    'depends': [
        'delivery', 
        'mail',
        'delivery_base_extra_options',
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/delivery_freightview_data.xml',
        'views/delivery_freightview.xml',
        'views/stock_picking_views.xml',
        'views/stock_quant_view.xml',
        'views/res_config_settings.xml',
        'wizard/choose_delivery_package_views.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'license': 'OPL-1',
    'installable': False,
    'price': '99.99',
    'currency': 'USD',
}
