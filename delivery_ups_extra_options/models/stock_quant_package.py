# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import models, fields, api, _

class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    currency_id = fields.Many2one('res.currency',related='picking_id.company_id.currency_id')
    ups_declared_value = fields.Monetary('UPS Declared Value')
    is_additional_handling = fields.Boolean("Additional Handling")
    is_hazmat = fields.Boolean("Hazmat")
    is_dry_ice = fields.Boolean("Dry Ice")
    ups_default_service_type = fields.Selection(related='picking_id.ups_default_service_type',string='UPS Service Type')