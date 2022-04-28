# Copyright 2018-2021 Sodexis
# License OEEL-1 (See LICENSE file for full copyright and licensing details).
from itertools import groupby
from odoo import models, _
from odoo.exceptions import UserError,ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):
        for order in self:
            picking_one_step=[]
            for key,group in groupby(order.picking_ids,lambda w_id: w_id.picking_type_id.warehouse_id):
                for pick in group:
                    if key.delivery_steps=='ship_only':
                        picking_one_step.append(pick.id)
            for picking in order.picking_ids.filtered(lambda pick: pick.id not in picking_one_step):
                picking_origin = ''
                if picking.picking_type_code == 'internal' and picking.state=='done':
                    picking_origin = picking.origin
                    for picking_out in order.picking_ids.filtered(lambda pick: pick.picking_type_code in ['outgoing','internal']):
                        if picking_out.origin == picking_origin and picking_out.state != 'done' and picking_out.id not in picking_one_step:
                            raise_error=True
                            return_dict={}
                            return_list=[]
                            for picking_return in order.picking_ids.filtered(lambda pick: 'Return' in pick.origin):
                                return_dict['id'] = picking_return.id
                                return_dict['origin'] = picking_return.origin
                                return_dict['state'] = picking_return.state
                                return_items = picking_return.mapped('move_line_ids')
                                if return_items:
                                    quantity_done=0
                                    for item in return_items:
                                        quantity_done+=item.qty_done
                                    return_dict['product_uom_qty'] = quantity_done
                                dictionary_copy_rt = return_dict.copy()
                                return_list.append(dictionary_copy_rt)
                            picking_dict={}
                            picking_list=[]
                            for pick_in in order.picking_ids.filtered(lambda pick: pick.picking_type_code in ['internal']):
                                if 'Return' not in pick_in.origin and pick_in.state in ['done']:
                                    picking_dict['id'] = pick_in.id
                                    picking_dict['origin'] = pick_in.origin
                                    picking_dict['state'] = pick_in.state
                                    picking_items = pick_in.mapped('move_line_ids')
                                    if picking_items:
                                        demand_items=0
                                        for item in picking_items:
                                            demand_items+=item.product_uom_qty_demand
                                        picking_dict['demand_items'] = demand_items
                                    elif len(return_list) != 0:
                                        picking_dict['raise_error'] = True
                                    dictionary_copy = picking_dict.copy()
                                    picking_list.append(dictionary_copy)
                                    if pick_in.state in ['done'] and len(return_list) == 0:
                                        raise ValidationError(
                                            _('This delivery items are about to deliver, so return the items and validate before cancel the order.'))
                            # if we did not validate the return DO
                            returned_items = 0
                            for return_data in return_list:
                                returned_items += return_data.get('product_uom_qty', 0)
                                if return_data['state'] != 'done':
                                    raise ValidationError(
                                        _('This delivery items are already returned and need to be validated to cancel the order.'))
                            # calculating total demand items and done items to check whether fully returned or not
                            demand_items = 0
                            raise_error = False
                            for picking_data in picking_list:
                                if 'demand_items' in picking_data:
                                    demand_items += picking_data['demand_items']
                                if 'raise_error' in picking_data:
                                    raise_error = True
                            if round(demand_items) != round(returned_items) and len(return_list) != 0:
                                raise ValidationError(
                                    _('All delivery items should be returned to cancel the order.(Check demand and reserved quantity)'))
                            # To check all the picking having return
                            if len(picking_list) != len(return_list) and len(return_list) != 0:
                                if round(demand_items) != round(returned_items) or raise_error == True:
                                    raise ValidationError(
                                        _('All the picked items are need to be returned and validated to cancel the order.'))
                            if len(return_list) == 0 and picking_out.state == 'cancel':
                                    raise ValidationError(
                                        _('This delivery items are picked already. Please return the items to cancel the order.'))
                            self = self.with_context(disable_cancel_warning=True)
        return super(SaleOrder, self).action_cancel()
