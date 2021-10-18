# -*- coding: utf-8 -*-
# Copyright 2020 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details)

import requests
import json

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from requests.auth import HTTPBasicAuth
from odoo import fields,_
from odoo.exceptions import UserError
import re
from odoo.http import request

# This re should match postcodes like 12345 and 12345-6789
ZIP_ZIP4 = re.compile('^[0-9]{5}(-[0-9]{4})?$')


def split_zip(zipcode):
    '''If zipcode is a ZIP+4, split it into two parts.
       Else leave it unchanged '''
    if ZIP_ZIP4.match(zipcode) and '-' in zipcode:
        return zipcode.split('-')
    else:
        return [zipcode, '']

class FreightViewRequest():

    def __init__(self, prod_environment=False, request_type="shipping", debug_logger=False):
        self.debug_logger = debug_logger
        if request_type == "shipping":
            if prod_environment:
                self.url = 'https://www.freightview.com/api/v1.0/shipments/'
            else:
                self.url = 'https://www.freightview.dev/api/v1.0/shipments/'
        elif request_type == "booking":
            if prod_environment:
                self.url = f"https://www.freightview.com/api/v1.0/book"
            else:
                self.url = f"https://www.freightview.dev/api/v1.0/book"
        else:
            if prod_environment:
                self.url = 'https://www.freightview.com/api/v1.0/rates'
            else:
                self.url = 'https://www.freightview.dev/api/v1.0/rates'
        self.prod_environment = prod_environment
        
    def _error_message(self, error_code):
        error_message = 'Freightview Server Not Found - Check your connectivity'
        if error_code == 400:
            error_message = _("Bad Request")
        elif error_code == 401:
            error_message = _("Authentication failed on the request.")
        elif error_code == 402:
            error_message = _("No active subscription with Freightview.")
        elif error_code == 404:
            error_message = _("The requested resource does not exist.")
        elif error_code == 500:
            error_message = _("The server encountered an error.")
        return error_message
    
    def check_required_value(self, carrier, warehouse, picking):
        shipper = warehouse.partner_id
        recipient = picking.partner_id
        recipient_required_field = ['name', 'city', 'zip', 'phone','state_id', 'country_id']
        if not recipient.street : 
            recipient_required_field.append('street')
            
        shipper_required_field = ['name', 'city', 'zip', 'phone', 'email', 'state_id', 'country_id']
        if not shipper.street :
            shipper_required_field.append('street')
            
        res = [field for field in shipper_required_field if not shipper[field]]
        if res:
            return _("The address of your company is missing or wrong!!! \n Missing field(s) :  %s", ", ".join(res).replace("_id", ""))
        if not ZIP_ZIP4.match(shipper.zip):
            return _("Please enter a valid ZIP code in your Company address")
        
        res = [field for field in recipient_required_field if not recipient[field]]
        if res:
            return _("The recipient address is missing or wrong!!! \n Missing field(s) :  %s", ", ".join(res).replace("_id", ""))
        product_name = []
        for move_line in picking.move_line_ids_without_package:
            if move_line and move_line.product_id and not move_line.product_id.weight:
                product_name.append(move_line.product_id.name)
        if product_name:
            return _("The product weight is missing or wrong!!! \n For the products(s) :  %s", ", ".join(product_name))     
        if not carrier.sudo().freightview_api_key:
            return _("Freightview Account Api Key is missing!!!")
        if not carrier.sudo().freightview_user_api_key:
            return _("Freightview User Api Key is missing!!!")
        return False
    
    def freightview_rate_request(self, carrier, picking, warehouse):
        params = self._freightview_rate_request_data(picking,warehouse)
        headers = {
            "Content-Type": "application/json"
        }
        dict_response = {}
        try:
            self.debug_logger(params, 'freightview_rate_request')
            req = requests.post(self.url, data=json.dumps(params),headers=headers, auth = HTTPBasicAuth(carrier.sudo().freightview_api_key, ''))
            req.raise_for_status()
            response_text = req.content
            self.debug_logger(response_text, 'freightview_rate_response')
            dict_response = json.loads(req.content.decode('utf-8'))             
            return dict_response
        except IOError:
            general_error_message = self._error_message(req.status_code)
            error_message = ''
            if req.content:
                error_message = json.loads(req.content.decode('utf-8')).get('message')
            dict_response['error'] = F"{general_error_message} - {error_message}"
            return dict_response 
    
    def freightview_book_shipment_request(self, carrier, selected_line, picking):
        rate_id = selected_line.rate_id
        params = {  "id": picking.freightview_shipment_id,
                    "rateId": rate_id,
        }
        headers = {
            "Content-Type": "application/json"
        }
        dict_response = {}
        try:
            self.debug_logger(params, 'freightview_book_shipment_request')
            req = requests.post(self.url, data=json.dumps(params),headers=headers, auth = HTTPBasicAuth(carrier.sudo().freightview_user_api_key, ''))
            req.raise_for_status()
            dict_response = json.loads(req.content.decode('utf-8'))
            response_text = req.content
            self.debug_logger(response_text, 'freightview_book_shipment_response')
            return dict_response
        except IOError as e:
            print(e)
            return dict_response

    def set_line_items(self,package):
        length = width = height = 0
        if package.packaging_id:
            if package.packaging_id.is_custom_dimensions:
                length = package.packaging_length
                width =  package.width
                height = package.height
            else:
                length = package.packaging_id.packaging_length
                width =  package.packaging_id.width
                height = package.packaging_id.height
        return {
                    'description': package.name,
                    'weight': package.shipping_weight,
                    'freightClass': package.ltl_class,
                    'length': length,
                    'width': width,
                    'height': height,
                    'package': 'Boxes',
                    'pieces': 1,
                    'nmfc': package.nmfc_item if package.nmfc_item else '',
                    'stackable': package.is_stackable,
                    'hazardous': package.is_hazmat,
                    'hazard': {
                                'hazmatId': package.hazmat_id,
                                'hazardClass': package.hazard_class
                            }
                }

    def _freightview_rate_request_data(self, picking, warehouse):  
        items = []
        if picking.has_packages:
            packages = picking.get_packages()
            for package in packages:
                items.append(self.set_line_items(package))
        else:
            items = picking.get_product_templates()
        company_name = picking.partner_id.name
        if picking.partner_id and picking.partner_id.commercial_company_name:
            company_name = picking.partner_id.commercial_company_name    
        charges = []
        if picking.is_liftgate_required_for_delivery:
            charges.append('liftgate delivery')
        if picking.is_inside_delivery_required:
            charges.append('inside delivery')
        if picking.is_call_or_notify_before_delivery:
            charges.append('arrival notice')
        if picking.is_delivery_appointment_required:
            charges.append('arrival schedule')
        if picking.is_sort_and_segregate:
            charges.append('sort and segregate')
        if picking.is_protect_from_freezing:
            charges.append('protect from freezing')
        rate_detail = {
            'pickupDate': datetime.strptime(str(picking.scheduled_date), f"{DF} %H:%M:%S").date().strftime("%Y-%m-%d"),
            'originCompany': warehouse.company_id.name,
            'originAddress': warehouse.partner_id.street,
#             'originAddress2': warehouse.partner_id.street2,
            'originCity': warehouse.partner_id.city,
            'originState': warehouse.partner_id.state_id.code,
            'originPostalCode': warehouse.partner_id.zip,
            'originCountry': warehouse.partner_id.country_id.code,
            'originType': 'business dock',
            'originContactName': warehouse.partner_id.name,
            'originContactPhone': warehouse.partner_id.phone,
            'originContactEmail': warehouse.partner_id.email,
            'originReferenceNumber': picking.name,
#             'originInstructions': 'Test Box',
            'originDockHoursOpen': '7:00 AM',  
            'originDockHoursClose': '7:00 PM',
            'destCompany': company_name,
            'destAddress': picking.partner_id.street,
#             'destAddress2': picking.partner_id.street2,
            'destCity': picking.partner_id.city,
            'destState': picking.partner_id.state_id.code,
            'destPostalCode': picking.partner_id.zip,
            'destCountry': picking.partner_id.country_id.code,
            'destType': 'residential' if picking.is_residential_address else 'business dock',
            'destContactName': picking.partner_id.name if picking.partner_id.name else '',
            'destContactPhone': picking.partner_id.phone if picking.partner_id.phone else '',
            'destContactEmail': picking.partner_id.email if picking.partner_id.email else '',
#             'destInstructions': 'Test Pack',
            'destDockHoursOpen': '7:00 AM',
            'destDockHoursClose': '7:00 PM',
            'emergencyName' : picking.partner_id.name if picking.partner_id.name else '',
            'emergencyPhone' : picking.partner_id.phone if picking.partner_id.phone else '',
            'items': items,
            'charges': charges,
        }
        return rate_detail
    
    def freightview_get_shipment_info_request(self, carrier, picking):
        dict_response = {}
        try:
            self.debug_logger('', 'freightview_get_shipping_request')
            req = requests.get(f"{self.url}{picking.freightview_shipment_id}", auth = HTTPBasicAuth(carrier.sudo().freightview_api_key, ''))
            req.raise_for_status()
            response_text = req.content
            self.debug_logger(response_text, 'freightview_get_shipping_response')
            dict_response = json.loads(req.content.decode('utf-8'))             
            return dict_response
        except IOError as e:
            general_error_message = self._error_message(req.status_code)
            error_message = ''
            if req.content:
                error_message = json.loads(req.content.decode('utf-8')).get('message')
            dict_response['error'] = F"{general_error_message} - {error_message}"
            return dict_response
        
    def freightview_get_all_shipment_info_request(self, carrier, picking, is_cron):
        dict_response = {}
        try:
            self.debug_logger('', 'freightview_get_shipping_request')
            if is_cron:
                url = f'{self.url.strip("/")}?createdDate={datetime.now().strftime("%Y-%m-%d")}'
            else:
                url = f'{self.url.strip("/")}?ref={picking.name}'
            req = requests.get(url, auth = HTTPBasicAuth(carrier.sudo().freightview_api_key, ''))
            req.raise_for_status()
            response_text = req.content
            self.debug_logger(response_text, 'freightview_get_shipping_response')
            dict_response = json.loads(req.content.decode('utf-8'))             
            return dict_response
        except IOError:
            general_error_message = self._error_message(req.status_code)
            error_message = ''
            if req.content:
                error_message = json.loads(req.content.decode('utf-8')).get('message')
            dict_response['error'] = F"{general_error_message} - {error_message}"
            return dict_response
        
        
