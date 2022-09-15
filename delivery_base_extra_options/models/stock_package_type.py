# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api

class PackageType(models.Model):
    _inherit = 'stock.package.type'

    is_custom_dimensions = fields.Boolean('Custom Dimensions',default=False)