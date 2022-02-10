# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

from .freightview_request import FreightViewRequest
from odoo import models,fields,_

class ProviderFreightView(models.Model):
    _inherit = 'delivery.carrier'
    
    delivery_type = fields.Selection(selection_add=[('freightview', "Freightview")],ondelete={'freightview': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    freightview_api_key = fields.Char(string='Freightview Account Api Key')
    freightview_user_api_key = fields.Char(string='Freightview User Api Key')
    notify_cost = fields.Float('Notify')
    appoint_cost = fields.Float('Appoint')
    blindshipping_cost = fields.Float('Blindshipping')
    freightview_overlength_rate_ids = fields.One2many('freightview.overlength.rate','delivery_id')

    def freightview_rate_shipment(self, picking):
        srm = FreightViewRequest(prod_environment=self.prod_environment, request_type = "rating", debug_logger=self.log_xml)
        warehouse = picking.picking_type_id.warehouse_id
        check_result = srm.check_required_value(self, warehouse, picking)        
        if check_result:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_result,
                    'warning_message': False}

        quote_response = srm.freightview_rate_request(self, picking, warehouse)

        if quote_response.get('error',False):
            return {
                    'success': False,
                    'data' : {} or False,
                    'error_message': _('Error:\n%s', quote_response.get('error',False)),
                    }

        return {
                'success': True,
                'data' : quote_response,
                'error_message': False,
                }
            
    
    def freightview_get_shipment_info(self, picking):
        srm = FreightViewRequest(prod_environment = self.prod_environment, debug_logger=self.log_xml)
        shipment_info_response = srm.freightview_get_shipment_info_request(self,picking)
        if shipment_info_response.get('error',False):
            return {
                    'success': False,
                    'data' : {} or False,
                    'error_message': _('Error:\n%s', shipment_info_response.get('error',False)),
                    }
        return {
                'success': True,
                'data' : shipment_info_response,
                'error_message': False,
                'warning_message': False
                }
    
    def freightview_get_all_shipment_info(self, picking=False, is_cron=False):
        srm = FreightViewRequest(prod_environment = self.prod_environment, debug_logger=self.log_xml)
        shipment_info_response = srm.freightview_get_all_shipment_info_request(self,picking,is_cron)
        if shipment_info_response.get('error',False):
            return {
                    'success': False,
                    'data' : {} or False,
                    'error_message': _('Error:\n%s', shipment_info_response.get('error',False)),
                    }
        return {
                'success': True,
                'data' : shipment_info_response,
                'error_message': False,
                'warning_message': False
                }

    def freightview_book_shipment(self, selected_line, picking):
        srm = FreightViewRequest(prod_environment=self.prod_environment, request_type = "booking", debug_logger=self.log_xml)
        warehouse = picking.picking_type_id.warehouse_id
        check_result = srm.check_required_value(self, warehouse, picking)
        if check_result:
            return {'success': False,
                    'price': 0.0,
                    'error_message': check_result,
                    'warning_message': False}
        book_shipment_response = srm.freightview_book_shipment_request(self, selected_line, picking)
        if book_shipment_response.get('error',False):
            return {
                    'success': False,
                    'data' : {} or False,
                    'error_message': _('Error:\n%s', book_shipment_response.get('error',False)),
                    }
        return {
                'success': True,
                'data' : book_shipment_response,
                'error_message': False,
                }
    
