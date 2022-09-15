# -*- coding: utf-8 -*-
# Copyright 2021-2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_ltl_class_value(self):
        return self.env['product.template']._fields['ltl_class'].selection

    is_residential_address = fields.Boolean("Residential Address")
    is_send_ups_declared_value = fields.Boolean("Send Declared Value", default=True)
    ups_declared_value = fields.Float('UPS Declared Value',compute='_compute_ups_declared_value')
    is_commercial_invoice_removal_indicator = fields.Boolean("Commercial Invoice Removal Indicator")
    is_hold_for_pickup =  fields.Boolean("Hold For Pickup Indicator")
    is_direct_delivery_only = fields.Boolean("Direct Delivery Only")
    is_saturday_delivery = fields.Boolean("Saturday Delivery")
    is_negotiated_rates  = fields.Boolean("Negotiated Rates", default=True)
    negotiated_price = fields.Float('Negotiated Price')
    ups_ground_freight_price = fields.Float('UPS Ground with Freight Pricing')
    ups_default_service_type = fields.Selection(related='carrier_id.ups_default_service_type',string='UPS Service Type')
    ltl_class = fields.Selection(_get_ltl_class_value,string='LTL Class')


    def _put_in_pack(self, move_line_ids, create_package_level=True):
        package = super(StockPicking,self)._put_in_pack(move_line_ids, create_package_level)
        if self._context.get('ups_declared_value'):
            package.ups_declared_value = self._context.get('ups_declared_value')
        if self._context.get('is_additional_handling'):
            package.is_additional_handling = self._context.get('is_additional_handling')
        if self._context.get('is_hazmat'):
            package.is_hazmat = self._context.get('is_hazmat')
        if self._context.get('is_dry_ice'):
            package.is_dry_ice = self._context.get('is_dry_ice')
        return package

    def _compute_ups_declared_value(self):
        for picking in self:
            ups_declared_value = 0.0
            if not picking.has_packages and picking.picking_type_code == 'outgoing':
                for move_line in picking.move_line_ids:
                    if move_line.qty_done:
                        ups_declared_value += move_line.qty_done * move_line.move_id.sale_line_id.price_unit
            picking.ups_declared_value = ups_declared_value

    def send_to_shipper(self):
        super(StockPicking,self).send_to_shipper()
        self.ensure_one()
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        if self.is_negotiated_rates and self.delivery_type == 'ups':
            msg =_(
                "Negotiated Cost received from UPS: %(negotiated_rate)s %(order_currency)s" ,
                negotiated_rate = self.negotiated_price,
                order_currency = order_currency.name
                )
            self.message_post(body=msg)
