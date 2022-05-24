# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    'name': "Vendor Bill Posting Based On Freightview Cost",
    'summary': """This module is used to import the estimated cost from freightview and post the vendor bill if estimated cost is greater than vendor bill amount""",
    'version': '14.0.1.0.0',
    'category': 'Uncategorized',
    'website': "http://sodexis.com/",
    'author': "Sodexis",
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'depends': [
        'account',
        'delivery_freightview',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/account_move_view.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'price': '39.99',
    'currency': 'USD',
}
