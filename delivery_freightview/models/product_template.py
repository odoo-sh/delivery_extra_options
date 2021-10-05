# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)
from odoo import models,fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_hazmat = fields.Boolean('Hazmat')