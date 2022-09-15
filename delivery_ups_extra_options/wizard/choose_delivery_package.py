# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = 'choose.delivery.package'

    @api.model
    def default_get(self, fields_list):
        defaults = super(ChooseDeliveryPackage,self).default_get(fields_list)
        if 'ups_declared_value' in fields_list:
            if defaults.get('picking_id'):
                picking = self.env['stock.picking'].browse(defaults.get('picking_id'))
                picking_move_lines = picking.move_line_ids
                if not picking.picking_type_id.show_reserved and not self.env.context.get('barcode_view'):
                    picking_move_lines = self.picking_id.move_line_nosuggest_ids
                move_line_ids = picking_move_lines.filtered(lambda ml:
                    float_compare(ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0
                    and not ml.result_package_id
                )
                if not move_line_ids:
                    move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.product_uom_qty, 0.0,
                                         precision_rounding=ml.product_uom_id.rounding) > 0 and float_compare(ml.qty_done, 0.0,
                                         precision_rounding=ml.product_uom_id.rounding) == 0)
                    shipping_weight = 0.0
                    for move_line in move_line_ids:
                        if move_line.product_id:
                                shipping_weight += move_line.product_id.weight*move_line.product_uom_qty
                    defaults['shipping_weight'] = shipping_weight
                ups_declared_value = 0.0
                if picking.ups_default_service_type not in ('92','93'):
                    for move_line in move_line_ids:
                        if move_line.qty_done:
                            ups_declared_value += move_line.qty_done * move_line.move_id.sale_line_id.price_unit
                        else:
                            ups_declared_value += move_line.product_qty * move_line.move_id.sale_line_id.price_unit
                defaults['ups_declared_value'] = ups_declared_value
        return defaults

    currency_id = fields.Many2one('res.currency',related='picking_id.company_id.currency_id')
    ups_declared_value = fields.Monetary('UPS Declared Value')
    is_additional_handling = fields.Boolean("Additional Handling")
    is_hazmat = fields.Boolean("Hazmat")
    is_dry_ice = fields.Boolean("Dry Ice")
    ups_default_service_type = fields.Selection(related='picking_id.ups_default_service_type',string='UPS Service Type')

    def action_put_in_pack(self):
        self = self.with_context(ups_declared_value=self.ups_declared_value, is_additional_handling=self.is_additional_handling, is_hazmat=self.is_hazmat,is_dry_ice=self.is_dry_ice)
        super(ChooseDeliveryPackage,self).action_put_in_pack()

    def get_package_value(self):
        values = super(ChooseDeliveryPackage,self).get_package_value()
        if self._context.get('ups_declared_value'):
            values.update({'ups_declared_value':self._context.get('ups_declared_value')})
        if self._context.get('is_additional_handling'):
            values.update({'is_additional_handling':self._context.get('is_additional_handling')})
        if self._context.get('is_dry_ice'):
            values.update({'is_dry_ice':self._context.get('is_dry_ice')})
        return values