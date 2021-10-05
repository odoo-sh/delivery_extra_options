# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    
    def _get_default_dimension_uom(self):
        package_dimension_uom_param = self.env['ir.config_parameter'].sudo().get_param('delivery_packages_dimension_uom.package_dimension_uom_id')
        package_dimension_uom = False
        if package_dimension_uom_param and package_dimension_uom_param.isdigit():
            package_dimension_uom_obj = self.env['uom.uom'].browse(int(package_dimension_uom_param))
            if package_dimension_uom_obj:
                package_dimension_uom = package_dimension_uom_obj.display_name
        return package_dimension_uom

    package_dimension_uom_name = fields.Char(
        compute='_compute_packages_dimension_uom_name', 
        default=_get_default_dimension_uom,
        string="Package Dimension UoM",
        )
    
    def _compute_packages_dimension_uom_name(self):
        for packaging in self:
            packaging.package_dimension_uom_name = self._get_default_dimension_uom()