# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import api, fields, models

class Company(models.Model):
    _inherit = 'res.company'

    ups_declared_value_limit = fields.Float('UPS Declared Value Limit',
                                            default=100.0,
                                            required=True, help="Insured Value Limit")