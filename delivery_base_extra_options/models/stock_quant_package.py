# copyright 2021 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo import models,fields,_

class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    def _get_ltl_class_value(self):
        return self.env['product.template']._fields['ltl_class'].selection

    def _get_default_length_uom(self):
        return self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    picking_id = fields.Many2one('stock.picking')
    ltl_class = fields.Selection(_get_ltl_class_value,
                                  string="LTL Class",
                                  help="Density class of product for LTL")
    is_hazmat = fields.Boolean("Hazmat")
    delivery_type = fields.Selection(related='picking_id.delivery_type', readonly=True)
    is_custom_dimensions = fields.Boolean(string='Custom Dimensions' ,related='packaging_id.is_custom_dimensions')
    height = fields.Integer('Height')
    width = fields.Integer('Width')
    packaging_length = fields.Integer('Length')
    length_uom_name = fields.Char(string='Length unit of measure label', compute='_compute_length_uom_name', default=_get_default_length_uom)
    package_dimension_uom_name = fields.Char(related='packaging_id.package_dimension_uom_name')

    def _compute_length_uom_name(self):
        for packaging in self:
            packaging.length_uom_name = self.env['product.template']._get_length_uom_name_from_ir_config_parameter()

    def action_view_picking(self):
        action = super(StockQuantPackage,self).action_view_picking()
        self.ensure_one()
        domain_array = action['domain'][0][2]
        if self.picking_id:
            picking = self.env['stock.picking'].browse(self.picking_id.id)
            if picking:
                domain_array += picking.ids
        action['domain'] = [('id','in',domain_array)]
        return action