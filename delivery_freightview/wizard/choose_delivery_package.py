# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing detail

from odoo import api, fields, models, _


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = 'choose.delivery.package'


    is_stackable = fields.Boolean('Stackable')
    nmfc_item = fields.Char('NMFC item #')
    is_hazmat = fields.Boolean('Hazmat')
    hazmat_id = fields.Char('Hazmat Id')
    hazard_class = fields.Selection([
                            ('1.1A', '1.1A'), ('1.1B', '1.1B'),
                            ('1.1C', '1.1C'), ('1.1D', '1.1D'),
                            ('1.1E', '1.1E'), ('1.1F', '1.1F'),
                            ('1.1G', '1.1G'), ('1.1J', '1.1J'),
                            ('1.1L', '1.1L'),
                            ('1.2B', '1.2B'), ('1.2C', '1.2C'), 
                            ('1.2D', '1.2D'), ('1.2E', '1.2E'), 
                            ('1.2F', '1.2F'), ('1.2G', '1.2G'), 
                            ('1.2H', '1.2H'), ('1.2J', '1.2J'),
                            ('1.2K', '1.2K'), ('1.2L', '1.2L'),
                            ('1.3C', '1.3C'), ('1.3F', '1.3F'), 
                            ('1.3G', '1.3G'), ('1.3H', '1.3H'), 
                            ('1.3J', '1.3J'), ('1.3K', '1.3K'), 
                            ('1.3L', '1.3L'),
                            ('1.4B', '1.4B'), ('1.4C', '1.4C'), 
                            ('1.4D', '1.4D'), ('1.4E', '1.4E'), 
                            ('1.4F', '1.4F'), ('1.4G', '1.4G'), 
                            ('1.4S', '1.4S'), ('1.5D', '1.5D'), 
                            ('1.6N', '1.6N'),
                            ('2.1', '2.1'), ('2.2', '2.2'), 
                            ('2.3', '2.3'), 
                            ('3', '3'), ('4.1', '4.1'), 
                            ('4.2', '4.2'), ('4.3', '4.3'),
                            ('5.1', '5.1'), ('5.2', '5.2'),
                            ('6.1', '6.1'), ('6.2', '6.2'),
                            ('6.3', '6.3'), ('7', '7'),
                            ('8', '8'), ('9', '9'),
                            ('9.2', '9.2'),
                                    ], 'Hazard Class', default='1.1A')
    delivery_type = fields.Selection(related='picking_id.delivery_type')

    def action_put_in_pack(self):
        self = self.with_context(is_stackable=self.is_stackable, nmfc_item=self.nmfc_item, hazmat_id=self.hazmat_id, hazard_class=self.hazard_class)
        super(ChooseDeliveryPackage,self).action_put_in_pack()

    def get_package_value(self):
        values = super(ChooseDeliveryPackage,self).get_package_value()
        if self.is_stackable:
            values.update({'is_stackable':self.is_stackable})
        if self.nmfc_item:
            values.update({'nmfc_item':self.nmfc_item})
        if self.hazmat_id:
            values.update({'hazmat_id':self.hazmat_id})
        if self.hazard_class:
            values.update({'hazard_class':self.hazard_class})
        return values
