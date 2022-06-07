# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import models,fields

class res_config_setting(models.TransientModel):
    _inherit = 'res.config.settings'

    other_delivery_instruction = fields.Char(string="Other Delivery Instruction",config_parameter = "delivery_freightview.other_delivery_instruction")