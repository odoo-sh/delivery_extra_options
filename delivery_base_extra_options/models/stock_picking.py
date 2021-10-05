# copyright 2021 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo import models,fields,api,_
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_ltl_class_value(self):
        return self.env['product.template']._fields['ltl_class'].selection

    ltl_class = fields.Selection(_get_ltl_class_value,string='LTL Class')
    is_residential_address = fields.Boolean("Residential Address")
    is_all_product_in_package = fields.Boolean(compute='_compute_is_all_product_in_package')

    @api.depends('move_line_ids', 'move_line_ids.result_package_id')
    def _compute_packages(self):
        super(StockPicking,self)._compute_packages()
        stock_quant_pack = self.env['stock.quant.package'].browse()
        for picking in self:
            picking.package_ids |= stock_quant_pack.search([('picking_id','=',picking.id)])

    def _compute_is_all_product_in_package(self):
        for picking in self:
            picking.is_all_product_in_package = False
            if all(True if move_line.result_package_id else False for move_line in picking.move_line_ids):
                picking.is_all_product_in_package = True

    def action_see_packages(self):
        action = super(StockPicking,self).action_see_packages()
        self.ensure_one()
        packages = self.env['stock.quant.package'].search([('picking_id','=',self.id)])
        domain_array = action['domain'][0][2]
        if packages:
            domain_array += packages.ids
        action['domain'] = [('id','in',domain_array)]
        action['context'] = {'picking_id': self.id}
        return action

    def action_add_a_package(self):
        self.ensure_one()
        view_id = self.env.ref('delivery.choose_delivery_package_view_form').id
        context = dict(
            self.env.context,
            current_package_carrier_type=self.carrier_id.delivery_type,
            default_picking_id=self.id
        )
        context['action_add_a_package'] = True
        if context['current_package_carrier_type'] in ['fixed', 'base_on_rule']:
            context['current_package_carrier_type'] = 'none'
        return {
            'name': _('Package Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.package',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    def _put_in_pack(self, move_line_ids, create_package_level=True):
        package = super(StockPicking,self)._put_in_pack(move_line_ids, create_package_level)
        if self._context.get('ltl_class'):
            package.ltl_class = self._context.get('ltl_class')
        if self._context.get('is_hazmat'):
            package.is_hazmat = self._context.get('is_hazmat')
        if self._context.get('height'):
            package.height = self._context.get('height')
        if self._context.get('width'):
            package.width = self._context.get('width')
        if self._context.get('length'):
            package.packaging_length = self._context.get('length')
        return package