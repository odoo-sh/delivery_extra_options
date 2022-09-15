# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import fields, models


class PackageType(models.Model):
    _inherit = 'stock.package.type'

    active = fields.Boolean(string="Active", default=True)