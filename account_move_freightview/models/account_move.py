# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api
from requests.auth import HTTPBasicAuth 
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    no_record_in_freightview = fields.Boolean(string='No Record in Freightview')
    freightview_estimated_cost = fields.Monetary("Freightview Estimated Cost")
    picking_id = fields.Many2one('stock.picking',copy=False)
    freightview_shipment_link = fields.Char('Freightview Shipment Link')
    checked_in_freightview = fields.Boolean(string='Checked in Freightview')
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        fields = result.get('fields')
        if view_type == 'form' and fields.get('picking_id'):
            fields['picking_id']['string'] = 'Deliver/Receipt'
        return result

    def cron_import_estimation_info_from_freightview(self):
        for move in self:
            move.get_estimation_info_from_freightview()

    def get_estimation_info_from_freightview(self):
        carrier = self.env.ref('delivery_freightview.delivery_carrier_freightview')
        if self.ref:
            if carrier.prod_environment:
                url = 'https://www.freightview.com/api/v1.0/shipments'
                shipment_url = F"https://www.freightview.com/app#shipments/"
            else:
                url = 'https://www.freightview.dev/api/v1.0/shipments'
                shipment_url = F"https://www.freightview.dev/app#shipments/"
            try:
                req = requests.get(f"{url}?pro={self.ref}", auth = HTTPBasicAuth(carrier.sudo().freightview_api_key, ''))
                req.raise_for_status()
                shipment = json.loads(req.content.decode('utf-8'))
                _logger.info(shipment)
                vals = {}
                picking = False
                no_record_in_freightview = True
                shipment_link = pro_num = shipper_reference = False
                estimated_cost = 0.0
                if shipment['shipments'] and shipment['shipments'][0]:
                    shipment_link = F"{shipment_url}{shipment['shipments'][0].get('id')}"
                    pro_num = shipment['shipments'][0].get('dispatch').get('proNum')
                    estimated_cost = shipment['shipments'][0].get('rate').get('total')
                    shipper_reference = shipment['shipments'][0].get('origin').get('referenceNumber')
                    no_record_in_freightview = False
                if shipper_reference:
                    picking = self.env['stock.picking'].search([('name','=',shipper_reference)])
                    if picking:
                        vals.update({
                                    'picking_id':picking.id
                                    })
                vals.update({
                            'checked_in_freightview': True,
                            'freightview_shipment_link':shipment_link,
                            'freightview_estimated_cost': estimated_cost,
                            'no_record_in_freightview':no_record_in_freightview
                            })
                self.write(vals)
                sale_ship_term_module = self.env['ir.module.module'].search([('name', '=', 'sale_ship_term'),('state','=','installed')])
                if sale_ship_term_module:
                    if picking and picking.sale_id and picking.sale_id.shipping_term not in ['collect','thirdparty']:
                        if pro_num and estimated_cost >= self.amount_total:
                            self.action_post()
                else:
                    if pro_num and estimated_cost >= self.amount_total:
                        self.action_post()
            except Exception as e:
                _logger.info(e)
                