# copyright 2021 Sodexis
# license OPL-1 (see license file for full copyright and licensing details).

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    ltl_class = fields.Selection([
                                    ("50", "50"),
                                    ("60", "60"),
                                    ("65", "65"),
                                    ("70", "70"),
                                    ("77.5", "77.5"),
                                    ("85", "85"),
                                    ("92.5", "92.5"),
                                    ("100", "100"),
                                    ("110", "110"),
                                    ("150", "150"),
                                    ("200", "200"),
                                    ("250", "250"),
                                ],
                                string="LTL Class",
                                help="Density class of product for LTL",
                                default="50")
    is_hazmat = fields.Boolean(string='Hazmat',default=False)