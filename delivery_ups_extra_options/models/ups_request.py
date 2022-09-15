# -*- coding: utf-8 -*-
# Copyright 2021 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).
from odoo.addons.delivery_ups.models.ups_request import UPSRequest
from zeep.exceptions import Fault

super_init = UPSRequest.__init__
super_check_required_value = UPSRequest.check_required_value
super_send_shipping = UPSRequest.send_shipping
super_set_package_detail = UPSRequest.set_package_detail
super_get_error_message = UPSRequest.get_error_message

class UPSRequestExtra(UPSRequest):

    def set_package_values(self,package,odoo_package=False):
        #Additional Handling
        if odoo_package and odoo_package.is_additional_handling:
            package.AdditionalHandling = odoo_package.is_additional_handling
            package.AdditionalHandlingIndicator = odoo_package.is_additional_handling

        package.PackageServiceOptions = self.factory_ns2.PackageServiceOptionsType()
        #Hazmat
        if odoo_package and odoo_package.is_hazmat and self.picking.ups_default_service_type not in ('92','93'):
            package.PackageServiceOptions.HazMat = self.factory_ns2.HazMatType()
            package.PackageServiceOptions.HazMat.ProperShippingName = 'Ground'
            package.PackageServiceOptions.HazMat.RegulationSet = 'CFR'
            package.PackageServiceOptions.HazMat.TransportationMode = 'Ground'
            package.PackageServiceOptions.HazMat.ClassDivisionNumber = '1'
            package.PackageServiceOptions.HazMat.Quantity = '1'
            package.PackageServiceOptions.HazMat.UOM = 'pound'
            package.PackageServiceOptions.HazMat.PackagingType = 'Fiberboard Box'
            package.PackageServiceOptions.HazMat.IDNumber = '123456'
        #Dry Ice
        if odoo_package and odoo_package.is_dry_ice:
            package.PackageServiceOptions.DryIce = self.factory_ns2.DryIceType()
            package.PackageServiceOptions.DryIce.RegulationSet = 'CFR'
            package.PackageServiceOptions.DryIce.DryIceWeight = self.factory_ns2.DryIceWeightType()
            package.PackageServiceOptions.DryIce.DryIceWeight.UnitOfMeasurement =  self.factory_ns2.ShipUnitOfMeasurementType()
            package.PackageServiceOptions.DryIce.DryIceWeight.UnitOfMeasurement.Code = '01'
            package.PackageServiceOptions.DryIce.DryIceWeight.Weight = odoo_package.shipping_weight

        if self.picking.is_commercial_invoice_removal_indicator:
            package.Description = 'Merchandise Decription'
        #Declared Value
        if self.picking.is_send_ups_declared_value and self.picking.ups_default_service_type not in ('92','93'):
            if odoo_package and self.picking.has_packages:
                if self.picking.company_id.ups_declared_value_limit:
                    if odoo_package.ups_declared_value > self.picking.company_id.ups_declared_value_limit:
                        declared_value = self.picking.company_id.ups_declared_value_limit
                    else:
                        declared_value = odoo_package.ups_declared_value
                else:
                    declared_value = odoo_package.ups_declared_value
            else:
                if self.picking.company_id.ups_declared_value_limit:
                    if self.picking.ups_declared_value > self.picking.company_id.ups_declared_value_limit:
                        declared_value = self.picking.company_id.ups_declared_value_limit
                    else:
                        declared_value = self.picking.ups_declared_value
                else:
                    declared_value = self.picking.ups_declared_value
            package.PackageServiceOptions.DeclaredValue = self.factory_ns2.PackageDeclaredValueType()
            package.PackageServiceOptions.DeclaredValue.CurrencyCode = self.picking.company_id.currency_id.name
            package.PackageServiceOptions.DeclaredValue.MonetaryValue = str(declared_value)
        if self.picking.carrier_id.ups_default_service_type == '03F':
            freight_class = False
            if odoo_package:
                freight_class = odoo_package.ltl_class
            else:
                freight_class = self.picking.ltl_class
            package.Commodity = self.factory_ns2.CommodityType()
            package.Commodity.FreightClass = freight_class


def __init__(self, debug_logger, username, password, shipper_number, access_number, prod_environment):
    self.picking = False
    return super_init(self, debug_logger, username, password, shipper_number, access_number, prod_environment)

def get_error_message(self, error_code, description):
    result = super_get_error_message(self, error_code, description)
    if result['error_message'] == 'None':
        result['error_message'] = description
    return result

def check_required_value(self, shipper, ship_from, ship_to, order=False, picking=False):
    if picking:
        self.picking = picking
    res = super_check_required_value(self, shipper, ship_from, ship_to, order, picking)
    if res and picking and picking.has_packages and 'The estimated price cannot be computed because the weight of your product' in res:
        res = False
    return res

def set_package_detail(self, client, packages, packaging_type, ship_from, ship_to, cod_info, request_type):
    Packages = super_set_package_detail(self, client, packages, packaging_type, ship_from, ship_to, cod_info, request_type)
    for ups_package_index, package in enumerate(Packages):
        if self.picking :
            for package_index, p in  enumerate(packages):
                for odoo_package_index, odoo_package in enumerate(self.picking.package_ids):
                    if ups_package_index == package_index == odoo_package_index and p.name == odoo_package.name:
                        UPSRequestExtra.set_package_values(self,package,odoo_package)
        if self.picking and not self.picking.has_packages:
            UPSRequestExtra.set_package_values(self,package)
    return Packages

def send_shipping(self, shipment_info, packages, shipper, ship_from, ship_to, packaging_type, service_type, saturday_delivery, duty_payment, cod_info=None, label_file_type='GIF', ups_carrier_account=False):
    if self.picking:
        if self.picking.carrier_id.ups_default_service_type == '03F':
            super_send_shipping(self, shipment_info, packages, shipper, ship_from, ship_to, packaging_type, service_type, saturday_delivery, duty_payment, cod_info, label_file_type, ups_carrier_account)
            shipment = self.shipment
            frs_payment_info = self.factory_ns2.FRSPaymentInfoType()
            frs_payment_info.Type = self.factory_ns2.PaymentType()
            partner_address = self.picking.partner_id
            ups_carrier_account = self.shipper_number
            frs_payment_info.Type.Code = "01"

            if self.picking.shipping_term == 'collect':
                frs_payment_info.Type.Code = "02"
                ups_carrier_account = self.picking.carrier_account
            if self.picking.shipping_term == 'thirdparty':
                ups_carrier_account = self.picking.carrier_account
                partner_address = self.picking.third_party_billing_id
                frs_payment_info.Type.Code = "03"
            if ups_carrier_account:
                frs_payment_info.AccountNumber = ups_carrier_account
                frs_payment_info.Address = self.factory_ns2.AccountAddressType()
                frs_payment_info.Address.PostalCode = partner_address.zip
                frs_payment_info.Address.CountryCode = partner_address.country_id.code or ''
                shipment.FRSPaymentInformation = frs_payment_info
                shipment.PaymentInformation = None

        else:

            ups_carrier_account = False
            if self.picking.shipping_term == 'collect':
                ups_carrier_account = self.picking.carrier_account
            super_send_shipping(self,shipment_info, packages, shipper, ship_from, ship_to, packaging_type, service_type, saturday_delivery, duty_payment, cod_info, label_file_type, ups_carrier_account)
            shipment = self.shipment
            if self.picking and self.picking.shipping_term == 'thirdparty' and self.picking.third_party_billing_id:
                ups_carrier_account = self.picking.carrier_account
                if ups_carrier_account:
                    shipcharge = self.factory_ns2.ShipmentChargeType()
                    shipcharge.Type = '01'
                    shipcharge.BillThirdParty = self.factory_ns2.BillThirdPartyChargeType()
                    shipcharge.BillThirdParty.Address = self.factory_ns2.AccountAddressType()
                    shipcharge.BillThirdParty.AccountNumber = ups_carrier_account
                    shipcharge.BillThirdParty.Address.PostalCode = self.picking.third_party_billing_id.zip
                    shipcharge.BillThirdParty.Address.CountryCode = self.picking.third_party_billing_id.country_id.code or ''
                    shipment.PaymentInformation.ShipmentCharge = [shipcharge]

def process_shipment(self):
    shipment =  self.shipment
    if self.picking:
        shipment.ShipmentServiceOptions = self.factory_ns2.ShipmentServiceOptionsType()
        #Residential Address
        if self.picking.is_residential_address:
            shipment.ShipTo.Address.ResidentialAddressIndicator = self.picking.is_residential_address
        #Saturday Delivery
        if self.picking.is_saturday_delivery:
            shipment.ShipmentServiceOptions.SaturdayDeliveryIndicator = 1
        #Commercial Invoice Removal Indicator
        if self.picking.is_commercial_invoice_removal_indicator:
            shipment.ShipmentServiceOptions.ImportControlIndicator = self.picking.is_commercial_invoice_removal_indicator
            shipment.ShipmentServiceOptions.CommercialInvoiceRemovalIndicator = self.picking.is_commercial_invoice_removal_indicator
            shipment.ShipmentServiceOptions.LabelMethod = self.factory_ns2.LabelMethodType()
            shipment.ShipmentServiceOptions.LabelMethod.Code = '05'
        #Hold For Pickup
        if self.picking.is_hold_for_pickup:
            shipment.ShipmentServiceOptions.HoldForPickupIndicator = self.picking.is_hold_for_pickup
        #Direct Delivery Only
        if self.picking.is_direct_delivery_only:
            shipment.ShipmentServiceOptions.DirectDeliveryOnlyIndicator = self.picking.is_direct_delivery_only

        #Negotiated Rates
        if self.picking.is_negotiated_rates:
            shipment.ShipmentRatingOptions = self.factory_ns2.RateInfoType()
            shipment.ShipmentRatingOptions.NegotiatedRatesIndicator = self.picking.is_negotiated_rates

        if shipment.Service.Code == '03F':
            shipment.ShipmentRatingOptions = self.factory_ns2.RateInfoType()
            shipment.ShipmentRatingOptions.FRSShipmentIndicator = True
            shipment.Service.Code = '03'

    client = self._set_client(self.ship_wsdl, 'Ship', 'ShipmentRequest')
    service = self._set_service(client, 'Ship')
    response = False
    try:
        if shipment.Service.Code == '93' or shipment.Service.Code == '92':
            with client.settings(strict=False, xsd_ignore_sequence_order=True):
                response = service.ProcessShipment(
                Request=self.request, Shipment=self.shipment,
                LabelSpecification=self.label)
        else:
            response = service.ProcessShipment(
                Request=self.request, Shipment=self.shipment,
                LabelSpecification=self.label)

        # Check if shipment is not success then return reason for that
        if not response:
            return {'error_message':'API Error'}
        if response.Response.ResponseStatus.Code != "1":
            return self.get_error_message(response.Response.ResponseStatus.Code, response.Response.ResponseStatus.Description)

        result = {}
        result['label_binary_data'] = {}
        for package in response.ShipmentResults.PackageResults:
            result['label_binary_data'][package.TrackingNumber] = self.save_label(package.ShippingLabel.GraphicImage, label_file_type=self.label_file_type)
        result['tracking_ref'] = response.ShipmentResults.ShipmentIdentificationNumber
        result['currency_code'] = response.ShipmentResults.ShipmentCharges.TotalCharges.CurrencyCode

        # Some users are qualified to receive negotiated rates
        negotiated_rate = 'NegotiatedRateCharges' in response.ShipmentResults and response.ShipmentResults.NegotiatedRateCharges and response.ShipmentResults.NegotiatedRateCharges.TotalCharge.MonetaryValue or None
        vals = {}
        if negotiated_rate:
            vals.update({'negotiated_price':negotiated_rate})
        netcharge = 'FRSShipmentData' in response.ShipmentResults and response.ShipmentResults.FRSShipmentData and response.ShipmentResults.FRSShipmentData.TransportationCharges and response.ShipmentResults.FRSShipmentData.TransportationCharges.NetCharge.MonetaryValue or None
        if netcharge:
            vals.update({'ups_ground_freight_price':netcharge})
        self.picking.write(vals)
        result['price'] = response.ShipmentResults.ShipmentCharges.TotalCharges.MonetaryValue
        return result

    except Fault as e:
        code = e.detail.xpath("//err:PrimaryErrorCode/err:Code", namespaces=self.ns)[0].text
        description = e.detail.xpath("//err:PrimaryErrorCode/err:Description", namespaces=self.ns)[0].text
        return self.get_error_message(code, description)
    except IOError as e:
        return self.get_error_message('0', 'UPS Server Not Found:\n%s' % e)

UPSRequest.__init__ = __init__
UPSRequest.check_required_value = check_required_value
UPSRequest.send_shipping = send_shipping
UPSRequest.set_package_detail = set_package_detail
UPSRequest.process_shipment = process_shipment
UPSRequest.get_error_message = get_error_message

