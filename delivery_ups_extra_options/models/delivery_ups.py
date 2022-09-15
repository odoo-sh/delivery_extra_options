# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import api, fields, models

class ProviderUPS(models.Model):
    _inherit = 'delivery.carrier'

    def _get_ups_service_types(self):
        values = super (ProviderUPS, self)._get_ups_service_types()
        if values:
            values.append(('93', 'UPS SurePost 1LB or greater'))
            values.append(('92', 'UPS SurePost Less than 1 lb'))
            values.append(('03F', 'UPS Ground with Freight Pricing'))

        return values
    ups_default_service_type = fields.Selection(_get_ups_service_types)
    ups_package_weight_unit = fields.Selection(selection_add=[('OZS', 'Ounces')])

    def _ups_convert_weight(self, weight, unit='KGS'):

        try:
            return super (ProviderUPS, self)._ups_convert_weight(weight, unit)
        except ValueError:
            if unit == 'OZS':
                weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
                return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_oz'), round=False)
            else:
                raise ValueError
