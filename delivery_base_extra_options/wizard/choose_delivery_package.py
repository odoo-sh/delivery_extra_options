# copyright 2021-2022 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare

class ChooseDeliveryPackage(models.TransientModel):
    _inherit = 'choose.delivery.package'

    def _get_default_length_uom(self):
        return self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    @api.model
    def default_get(self, fields_list):
        defaults = super(ChooseDeliveryPackage,self).default_get(fields_list)
        ltl_class_array = []
        defaults['is_add_a_package_action'] = False
        if 'is_hazmat' or 'ltl_class' in fields_list and defaults.get('picking_id'):
            picking = self.env['stock.picking'].browse(defaults.get('picking_id'))
            is_hazmat = False
            picking_move_lines = picking.move_line_ids
            if picking:
                selected_move_lines = picking_move_lines.filtered(lambda x:not x.result_package_id and x.qty_done > 0)
                if selected_move_lines:
                    for move_line in selected_move_lines:
                        if move_line.product_id.product_tmpl_id.ltl_class:
                            ltl_class_array.append(move_line.product_id.product_tmpl_id.ltl_class)
                else:
                    for move_line in picking.move_line_ids.filtered(lambda x:not x.result_package_id):
                        if move_line.product_id.product_tmpl_id.ltl_class:
                            ltl_class_array.append(move_line.product_id.product_tmpl_id.ltl_class)
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
            hazmat_move_lines = move_line_ids.filtered(lambda x: x.product_id.is_hazmat)
            if hazmat_move_lines:
                is_hazmat = True
            defaults['is_hazmat'] = is_hazmat
        if ltl_class_array:
            ltl_class = max(ltl_class_array)
            defaults['ltl_class'] = ltl_class
        if self._context.get('action_add_a_package'):
            defaults['is_add_a_package_action'] = True
        return defaults

    def _get_ltl_class_value(self):
        return self.env['product.template']._fields['ltl_class'].selection

    ltl_class = fields.Selection(_get_ltl_class_value,
                                  string="LTL Class",
                                  help="Density class of product for LTL")
    is_hazmat = fields.Boolean("Hazmat")
    delivery_type = fields.Selection(related='picking_id.delivery_type', readonly=True)
    is_custom_dimensions = fields.Boolean(string='Custom Dimensions' ,related='delivery_package_type_id.is_custom_dimensions')
    height = fields.Integer(string='Height')
    width = fields.Integer(string='Width')
    packaging_length = fields.Integer(string='Length')
    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name', default=_get_default_length_uom)
    package_dimension_uom_name = fields.Char(related='delivery_package_type_id.package_dimension_uom_name')
    quantity = fields.Integer("Quantity",default="1")
    is_add_a_package_action = fields.Boolean()

    @api.onchange('delivery_package_type_id')
    def onchange_delivery_package_type_id(self):
        if self.delivery_package_type_id:
            self.height = self.delivery_package_type_id.height
            self.width  = self.delivery_package_type_id.width
            self.packaging_length  = self.delivery_package_type_id.packaging_length

    def _compute_length_uom_name(self):
        for packaging in self:
            packaging.length_uom_name = self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    def action_put_in_pack(self):
        self = self.with_context(is_hazmat=self.is_hazmat,ltl_class=self.ltl_class,height=self.height, width=self.width, length=self.packaging_length)
        if self._context.get('action_add_a_package'):
            self.action_add_a_package()
        else:
            super(ChooseDeliveryPackage,self).action_put_in_pack()

    def get_package_value(self):
        values = {}
        values.update({'picking_id':self.picking_id.id})
        if self.delivery_package_type_id:
            values.update({'package_type_id':self.delivery_package_type_id.id})
        if self.ltl_class:
            values.update({'ltl_class':self.ltl_class})
        if self._context.get('is_hazmat'):
            values.update({'is_hazmat':self._context.get('is_hazmat')})
        if self.shipping_weight:
            values.update({'shipping_weight':self.shipping_weight})
        if self._context.get('height'):
            values.update({'height':self._context.get('height')})
        if self._context.get('width'):
            values.update({'width':self._context.get('width')})
        if self._context.get('length'):
            values.update({'packaging_length':self._context.get('length')})
        return values

    def action_add_a_package(self):
        values = self.get_package_value()
        for i in range(0,self.quantity):
            self.env['stock.quant.package'].create(values)
        return True
