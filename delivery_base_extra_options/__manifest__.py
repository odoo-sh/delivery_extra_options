# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Delivery Base Extra Options",
    "summary": """This module offers the basic delivery options available across all carrier(s).""",
    "version": "15.0.1.0.0",
    "category": "Inventory/Delivery",
    "website": "http://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "depends": [
        'stock',
        'delivery',
        'delivery_packages_dimension_uom'
    ],
    "data": [
        "wizard/choose_delivery_package_view.xml",
        "views/product_template_view.xml",
        "views/product_packaging_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_quant_package_view.xml",
    ],
    'images': ['images/main_screenshot.png'],
}
