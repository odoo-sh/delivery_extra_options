# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    fedex_signature_option_type = fields.Selection([('adult', 'Adult'), ('direct', 'Direct')],string='Signature Type')