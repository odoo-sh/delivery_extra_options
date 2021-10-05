# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    is_custom_dimensions = fields.Boolean('Custom Dimensions',default=False)