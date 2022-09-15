# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, api

class PackageType(models.Model):
    _inherit = 'stock.package.type'

    @api.onchange('is_custom_dimensions')
    def _onchange_delivery_carrier_custom(self):
        if self.is_custom_dimensions and self.package_carrier_type=='ups' and not self.shipper_package_code:
            self.shipper_package_code = '02'

    @api.onchange('package_carrier_type')
    def _onchange_carrier_type(self):
        if self.is_custom_dimensions and self.package_carrier_type=='ups' and self.shipper_package_code:
            return
        return super(PackageType,self)._onchange_carrier_type()