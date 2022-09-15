# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ups_declared_value_limit = fields.Float(related='company_id.ups_declared_value_limit',
                                            string="UPS Declared Value Limit",readonly=False,
                                            help="Insured Value Limit")