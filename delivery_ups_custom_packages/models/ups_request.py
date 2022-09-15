# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo.addons.delivery_ups.models.ups_request import Package
from odoo.http import request

super_init = Package.__init__

def __init__(self, carrier, weight, quant_pack=False, name=''):
    res = super_init(self, carrier, weight, quant_pack, name)
    if quant_pack:
        package = request.env['stock.quant.package'].search([('name', '=', name)], limit=1)
        if package:
            self.dimension = {'length': package.packaging_length, 'width': package.width, 'height': package.height}
    return res

Package.__init__ = __init__

