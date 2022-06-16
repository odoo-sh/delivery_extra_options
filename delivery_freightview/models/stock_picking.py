# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)
from odoo import models,fields,api,_
from odoo.exceptions import UserError
import json
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import ValidationError

class Picking(models.Model):
    _inherit = 'stock.picking'

    is_quote_created_in_freightview = fields.Boolean('Is Quote Created In Freightview', copy=False)
    freightview_shipment_id = fields.Char('Freightview Shipment ID',copy=False)
    is_imported_shipment_info_from_freightview = fields.Boolean('Is Imported Data From Freightview', copy=False)
    is_call_or_notify_before_delivery = fields.Boolean('Call/Notify Before Delivery', copy=False)
    is_delivery_appointment_required = fields.Boolean('Delivery Appointment Required', copy=False)
    is_sort_and_segregate = fields.Boolean('Sort And Segregate', copy=False)
    is_protect_from_freezing = fields.Boolean('Protect From Freezing', copy=False)
    is_liftgate_required_for_delivery = fields.Boolean('Liftgate Required For Delivery', copy=False)
    is_inside_delivery_required = fields.Boolean('Inside Delivery Required', copy=False)
    is_hazmat = fields.Boolean('Hazmat', compute='_compute_is_hazmat', store=True)
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
    is_stackable = fields.Boolean('Stackable')
    nmfc_item = fields.Char('NMFC item #')
    is_residential_address = fields.Boolean("Residential Address")
    freightview_shipment_rate_ids = fields.One2many('freightview.shipment.rate','picking_id')
    is_freightview_shipment_rate_selected = fields.Boolean(compute='_compute_is_rate_selected')
    is_notify = fields.Boolean('Notify')
    is_appoint = fields.Boolean('Appoint')
    other_delivery_instruction = fields.Char(string="Other Delivery Instruction")
    actual_carrier_name = fields.Char(string="Actual Carrier Name",readonly = True,store = True)

    def create(self, vals):
        picking_type_id = vals.get('picking_type_id',False)
        if picking_type_id:
            picking_type_code = self.env['stock.picking.type'].browse(picking_type_id).code
            if picking_type_code == 'outgoing':
                irc_sudo = self.env['ir.config_parameter'].sudo()
                other_delivery_instruction = irc_sudo.get_param('delivery_freightview.other_delivery_instruction')
                if other_delivery_instruction:
                    vals.update({'other_delivery_instruction': other_delivery_instruction})
        res = super(Picking, self).create(vals)
        return res

    def _compute_is_rate_selected(self):
        is_selected = any([x.is_selected for x in self.freightview_shipment_rate_ids])
        self.is_freightview_shipment_rate_selected = is_selected

    @api.onchange('freightview_shipment_rate_ids')
    def _onchange_is_selected(self):
        booked_count = 0
        for rec in self.freightview_shipment_rate_ids:
            if rec.is_selected:
                booked_count += 1
        if booked_count > 1:
            return {"warning": {"title": _("Warning"), "message": "Please select only one shipment service"}}

    def send_to_shipper(self):
        self.ensure_one()
        if self.carrier_id and self.carrier_id.delivery_type != 'freightview':
            super(Picking,self).send_to_shipper()

    def button_validate(self):
        for picking in self:
            carrier = picking.carrier_id
            if (
                not picking.carrier_tracking_ref and carrier
                and carrier.delivery_type == 'freightview'
                and picking.picking_type_code == 'outgoing'
            ):
                result = carrier.freightview_get_all_shipment_info(picking)
                if result.get('success', False):
                    for shipment in result.get('data').get('shipments'):
                        picking.update_delivery_order(shipment)
        #                     picking.log_package_details_internal_note(shipment)
        return super(Picking, self).button_validate()

    @api.depends('move_ids_without_package')
    def _compute_is_hazmat(self):
        is_hazmat = any([move_line.product_id.product_tmpl_id.is_hazmat for move_line in self.move_line_ids])
        self.is_hazmat = is_hazmat

    @api.depends('state')
    def _compute_show_validate(self):
        super(Picking,self)._compute_show_validate()
        for picking in self:
            if picking.delivery_type == 'freightview' and picking.picking_type_code == 'outgoing' :
                if not picking.is_quote_created_in_freightview:
                    picking.show_validate = False
                if not picking.is_imported_shipment_info_from_freightview:
                    picking.show_validate = False
                if picking.is_imported_shipment_info_from_freightview and picking.state == 'assigned':
                    picking.show_validate = True

    def view_quote_in_freightview(self):
        carrier = self.carrier_id
        if carrier and carrier.delivery_type == 'freightview' and self.picking_type_code == 'outgoing':
            if not carrier.prod_environment:
                redirect_url = f"https://www.freightview.dev/app#quote/{self.freightview_shipment_id}/rates"
            else:
                redirect_url = f"https://www.freightview.com/app#quote/{self.freightview_shipment_id}/rates"
            return {
                'type': 'ir.actions.act_url',
                'url':  redirect_url ,
                'target': 'new'
                }
        return True

    def view_shipment_in_freightview(self):
        carrier = self.carrier_id
        if carrier and carrier.delivery_type == 'freightview' and self.picking_type_code == 'outgoing':
            if not carrier.prod_environment:
                redirect_url = f"https://www.freightview.dev/app#shipments/{self.freightview_shipment_id}"
            else:
                redirect_url = f"https://www.freightview.com/app#shipments/{self.freightview_shipment_id}"
            return {
                'type': 'ir.actions.act_url',
                'url':  redirect_url ,
                'target': 'new'
                }
        return True

    def create_quote_in_freightview(self,create_quote_button=True):
        carrier = self.carrier_id
        if carrier and carrier.delivery_type == 'freightview' and self.picking_type_code == 'outgoing':
            result = carrier.freightview_rate_shipment(self)
            if result.get('success',False):
                freightview_shipment_rate_obj = self.env['freightview.shipment.rate']
                freightview_shipment_id = result.get('data').get('id')
                self.freightview_shipment_id = freightview_shipment_id
                self.is_quote_created_in_freightview = True
                if create_quote_button:
                    return {
                    'type': 'ir.actions.act_url',
                    'url':  result.get('data').get('links').get('ratesUrl') ,
                    'target': 'new'
                    }
                else:
                    rates = result.get('data').get('rates')
                    for rate in rates:
                        if rate.get('status') == 'ok':
                            charges = rate.get('charges')
                            residential_delivery = 0
                            hazardous = 0
                            fuel = 0
                            linehaul = 0
                            over_dimension = 0
                            overlength_fee = 0
                            notify = 0
                            appoint = 0
                            blindshipping = 0
                            total = 0
                            diff_amount = 0
                            carrier = self.env['delivery.carrier'].search([('name', 'ilike', '%' + rate.get('carrier') + '%')], limit=1)
                            connector_freight_quote_module = self.env['ir.module.module'].sudo().search([('name', '=', 'connector_freight_quote')])
                            if connector_freight_quote_module.state == 'installed':
                                surcharge_ids = self.group_id.sale_id.rate_surcharge_ids
                            for charge in charges:
                                if charge['name']=='residential delivery':
                                    residential_delivery=charge['amount']
                                if charge['name']=='hazardous':
                                    hazardous=charge['amount']
                                if charge['name']=='fuel':
                                    fuel=charge['amount']
                                if charge['name']=='linehaul':
                                    linehaul=charge['amount']
                                if charge['name']=='discount':
                                    discount=charge['amount']
                                if charge['name']=='arrival notice':
                                    notify=charge['amount']
                                if charge['name']=='arrival schedule':
                                    appoint=charge['amount']
                                if charge['name']=='over dimension':
                                    over_dimension=charge['amount']
                            if carrier and carrier.notify_cost:
                                if self.is_notify:
                                    notify = carrier.notify_cost
                                else:
                                    for surcharge in surcharge_ids:
                                        if surcharge.display_name=='notify':
                                            notify = carrier.notify_cost
                            if carrier and carrier.appoint_cost:
                                if self.is_appoint:
                                    appoint = carrier.appoint_cost
                                else:
                                    for surcharge in surcharge_ids:
                                        if surcharge.display_name=='appoint':
                                            appoint = carrier.appoint_cost
                            if over_dimension:
                                length_list = self.package_ids.mapped('packaging_length')
                                for length in length_list:
                                    freightview_overlength_rate = carrier.freightview_overlength_rate_ids.filtered(lambda x: length >= x.min_value and length <= x.max_value)
                                    if freightview_overlength_rate:
                                        overlength_fee += freightview_overlength_rate.fee
                                    else:
                                        freightview_overlength_rate = carrier.freightview_overlength_rate_ids.sorted(key = 'max_value', reverse = True)
                                        if freightview_overlength_rate and freightview_overlength_rate[0]:
                                            if length > freightview_overlength_rate[0].max_value:
                                                overlength_fee += freightview_overlength_rate[0].fee
                            if carrier and (self.drop_shipping or self.group_id.sale_id.drop_shipping):
                                blindshipping = carrier.blindshipping_cost
                            accessorial_charges = (notify + appoint + blindshipping + overlength_fee)
                            total =  (rate.get('total') - over_dimension) + accessorial_charges
                            diff_amount =  accessorial_charges
                            freightview_shipment_rate_obj.create({
                                            'rate_id':rate.get('id'),
                                            'carrier':rate.get('carrier'),
                                            'service_type': rate.get('serviceType'),
                                            'estimated_days': rate.get('days'),
                                            'pickup_date': result.get('data').get('pickupDate'),
                                            'total': total,
                                            'book_url':rate.get('bookUrl'),
                                            'linehaul_charge': linehaul,
                                            'fuel_charge': fuel,
                                            'residential_delivery_charge': residential_delivery,
                                            'hazardous_charge': hazardous,
                                            'blindshipping_charge': blindshipping,
                                            'notify_charge': notify,
                                            'appoint_charge': appoint,
                                            'over_dimension_charge': overlength_fee,
                                            'picking_id': self.id,
                                            'difference_amount': diff_amount
                                            })
                    freightview_shipment_rate = freightview_shipment_rate_obj.search([('picking_id','=',self.id)],order='total asc', limit=1)
                    freightview_shipment_rate.write({'is_selected':True})
            else:
                raise UserError(_(result.get('error_message',False)))
        return True

    def get_shipment_info_from_freightview(self):
        carrier = self.carrier_id
        if carrier and carrier.delivery_type == 'freightview' and self.picking_type_code == 'outgoing':
            result = carrier.freightview_get_shipment_info(self)
            if result.get('success',False):
                self.update_delivery_order(result.get('data'))
#                 self.log_package_details_internal_note(result.get('data'))
            else:
                result = carrier.freightview_get_all_shipment_info(self)
                if result.get('success',False):
                    for shipment in result.get('data').get('shipments'):
                        self.update_delivery_order(shipment)
#                         self.log_package_details_internal_note(shipment)
                else:
                    raise UserError(_(result.get('error_message',False)))
        return True

    def get_rates_in_freightview(self):
        if not self.freightview_shipment_rate_ids:
            self.create_quote_in_freightview(create_quote_button=False)
            if self.freightview_shipment_rate_ids:
                for carrier in self.freightview_shipment_rate_ids:
                    if carrier.is_selected == True:
                        self.actual_carrier_name = carrier.carrier
                        break
        return True

    def review_quote_in_freightview(self):
        selected_lines = self.freightview_shipment_rate_ids.filtered(lambda x: x.is_selected)
        if len(selected_lines) != 1:
            raise UserError(_("Please select only one shipment service"))
        rate_url = selected_lines[0].book_url
        return {
                'type': 'ir.actions.act_url',
                'url':  rate_url ,
                'target': 'new'
                }
        return True

    def reset_and_clear(self):
        if not self.is_imported_shipment_info_from_freightview:
            self.freightview_shipment_id = False
            self.is_quote_created_in_freightview = False
            self.write({
                'freightview_shipment_rate_ids':[(5,0,0)]
            })
            self.actual_carrier_name = False

    def book_in_freightview(self):
        self.get_shipment_info_from_freightview()
        if self.carrier_tracking_ref and self.is_imported_shipment_info_from_freightview:
            notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Shipment Already Booked.'),
                'type': 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
                },
            }
            return notification
        if not self.carrier_tracking_ref and not self.is_imported_shipment_info_from_freightview:
            selected_lines = self.freightview_shipment_rate_ids.filtered(lambda x: x.is_selected)
            if len(selected_lines) != 1:
                raise UserError(_("Please select only one shipment service"))
            result = self.carrier_id.freightview_book_shipment(selected_lines, self)
            if result.get('success',False):
                dict_response = result.get('data')
                if dict_response:
                    selected_lines.write({'status':'booked'})
                    self.update_delivery_order(dict_response)
            else:
                raise UserError(_(result.get('error_message',False)))

    def update_delivery_order(self,shipment,cron=False):
        picking = self
        if cron:
            picking = self.search([('name','=', shipment.get('origin').get('referenceNumber'))])
        if picking:
            if shipment.get('rate').get('mode') == 'Parcel':
                picking.carrier_tracking_ref = shipment.get('dispatch').get('trackingNum')
            if shipment.get('rate').get('mode') == 'LTL':
                picking.carrier_tracking_ref = shipment.get('dispatch').get('proNum')
            picking.carrier_price = shipment.get('rate').get('total')
            picking.is_imported_shipment_info_from_freightview = True
            picking.freightview_shipment_id = shipment.get('id')
            picking.actual_carrier_name = shipment.get('dispatch').get('carrier')

    def log_package_details_internal_note(self,shipment):
        if shipment.get('items'):
            message = ''
            package_count = 0
            for item in shipment.get('items'):
                package_count = package_count+1
                message += '''Package      : %s <br/><br/>
                              Product      : %s <br/>
                              Freight Class : %s <br/>
                              Weight       : %s <br/>
                              Length       : %s <br/>
                              Width        : %s <br/>
                              Height       : %s <br/>
                              Package Type : %s <br/>
                              Peices       : %s <br/>
                              NMFC         : %s <br/><br/>'''% (package_count, item.get('description'), item.get('freightClass'),
                                                           item.get('weight'), item.get('length'), item.get('width'),
                                                           item.get('height'),item.get('package'),item.get('pieces'),item.get('nmfc'))
        if message:
            self.message_post(body=message,
                              message_type='comment',
                              subtype_xmlid='mail.mt_note')

    def cron_import_shipment_info_from_freightview(self):
        carrier = self.env.ref('delivery_freightview.delivery_carrier_freightview')
        result = carrier.freightview_get_all_shipment_info(is_cron=True)
        if result.get('success',False):
            for shipment in result.get('data').get('shipments'):
                self.update_delivery_order(shipment,cron=True)
        else:
            raise UserError(_(result.get('error_message',False)))
        return True

    def cron_import_package_info_from_freightview(self):
        pickings = self.search([('state', '=', 'done'),('carrier_tracking_ref','!=',False),('carrier_id.delivery_type' , '=', 'freightview'),('picking_type_id.code','=','outgoing')])
        for picking in pickings:
            result = picking.carrier_id.freightview_get_all_shipment_info(picking)
            if result.get('success',False):
                for shipment in result.get('data').get('shipments'):
                    picking.log_package_details_internal_note(shipment)

    def get_packages(self):
        quant_package = self.env['stock.quant.package']
        package_ids = self.move_line_ids.mapped('result_package_id').ids
        package_ids += quant_package.search([('picking_id','=',self.id)]).ids
        return quant_package.search([('id','in',package_ids)])

    def get_product_templates(self):
        items = []
        move_line_ids = self.move_line_ids
        ltl_class_array = [move_line.product_id.product_tmpl_id.ltl_class for move_line in move_line_ids]
        ltl_class_unique = list(set(ltl_class_array))
        for ltl_class in ltl_class_unique:
            filtered_move_line_ids = self.move_line_ids.filtered(lambda x:x.ltl_class == ltl_class)
            product_name = ''
            shipping_weight = 0.0
            for move_line in filtered_move_line_ids:
                product_name += move_line.product_id.name+", "
                shipping_weight += move_line.product_id.weight
            items.append({
                'description': product_name.strip(", "),
                'weight': shipping_weight,
                'freightClass': ltl_class,
                'length': 48,
                'width': 48,
                'height': 48,
                'package': 'Boxes',
                'pieces': 1,
                'hazardous': self.is_hazmat,
                'hazard': {
                                'hazmatId': self.hazmat_id or '',
                                'hazardClass': self.hazard_class
                            },
                'stackable': self.is_stackable,
                'nmfc': self.nmfc_item or '',
            })
        return items

    def _put_in_pack(self, move_line_ids, create_package_level=True):
        package = super(Picking,self)._put_in_pack(move_line_ids, create_package_level)
        if self._context.get('is_stackable'):
            package.is_stackable = self._context.get('is_stackable')
        if self._context.get('nmfc_item'):
            package.nmfc_item = self._context.get('nmfc_item')
        if self._context.get('hazmat_id'):
            package.hazmat_id = self._context.get('hazmat_id')
        if self._context.get('hazard_class'):
            package.hazard_class = self._context.get('hazard_class')
        return package
