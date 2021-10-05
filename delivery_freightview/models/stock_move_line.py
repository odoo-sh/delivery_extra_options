# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)
from odoo import models,fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    ltl_class = fields.Selection(related='product_id.product_tmpl_id.ltl_class')