# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

from odoo import models,fields,_,api
from odoo.exceptions import ValidationError

class FreightviewShipmentRate(models.Model):
    _name = 'freightview.shipment.rate'
    _description = "Freightview Shipment Rate"

    rate_id = fields.Char('Rate ID')
    carrier = fields.Char()
    service_type = fields.Char()
    estimated_days = fields.Integer()
    pickup_date = fields.Date()
    total = fields.Float()
    sequence = fields.Integer(string='Sequence', default=10)
    book_url = fields.Char('Book URL')
    is_selected = fields.Boolean('Selected')
    linehaul_charge = fields.Float('Line haul Charge')
    fuel_charge = fields.Float('Fuel Charge')
    residential_delivery_charge = fields.Float('Residential Charge')
    hazardous_charge = fields.Float('Hazardous Charge')
    status = fields.Selection(selection=[('draft','Draft'),('booked','Booked')], string='Status', default='draft')
    picking_id = fields.Many2one('stock.picking')