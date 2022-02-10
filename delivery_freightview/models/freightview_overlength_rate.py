# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

from odoo import models,fields,_,api
from odoo.exceptions import ValidationError

class FreightviewOverlengthRate(models.Model):
    _name = 'freightview.overlength.rate'
    _description = "Freightview Overlength Rate"

    min_value = fields.Integer()
    max_value = fields.Integer()
    fee = fields.Integer()
    delivery_id = fields.Many2one('delivery.carrier')
    
    @api.onchange('min_value')
    def onchange_min_value(self):
        if self.max_value != 0 and self.min_value > self.max_value:
            raise ValidationError("Can't be greater than max value")
 
    @api.onchange('max_value')
    def onchange_max_value(self):
        if self.min_value != 0 and self.max_value < self.min_value:
            raise ValidationError("Can't be lesser than min value")
        