# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    package_dimension_uom_id = fields.Many2one('uom.uom', 
                                               config_parameter='delivery_packages_dimension_uom.package_dimension_uom_id',
                                               string="Package Dimension UoM")
    
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        if self.package_dimension_uom_id:
            self.env['ir.config_parameter'].sudo().set_param('delivery_packages_dimension_uom.package_dimension_uom_id', (self.package_dimension_uom_id.id or ''))
        return res
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        package_dimension_uom_id = self.env.ref("delivery_packages_dimension_uom.package_dimension_uom_id", None)
        if package_dimension_uom_id:
            res.update({
                'package_dimension_uom_id': package_dimension_uom_id.id,
            })
        return res
    