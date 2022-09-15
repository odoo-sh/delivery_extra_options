# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    active = fields.Boolean(string="Active", default=True)