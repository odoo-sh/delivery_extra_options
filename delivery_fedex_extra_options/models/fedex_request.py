# -*- coding: utf-8 -*-
# Copyright 2022 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

import logging
from odoo.addons.delivery_fedex.models.fedex_request import FedexRequest
from odoo.http import request

_logger = logging.getLogger(__name__)

super_init = FedexRequest.__init__
super_transaction_detail = FedexRequest.transaction_detail
super_shipping_charges_payment = FedexRequest.shipping_charges_payment


def __init__(self, debug_logger, request_type="shipping", prod_environment=False, ):
    self.picking = False
    return super_init(self, debug_logger, request_type="shipping", prod_environment=False, )
        
def transaction_detail(self, transaction_id):
    if transaction_id and isinstance(transaction_id,int):
        self.picking = request.env['stock.picking'].browse(transaction_id)
    return super_transaction_detail(self, transaction_id)

def shipping_charges_payment(self, shipping_charges_payment_account):
    super_shipping_charges_payment(self, shipping_charges_payment_account)
    if self.picking:
        if self.picking.shipping_term in ['collect']:
            self.RequestedShipment.ShippingChargesPayment = self.factory.Payment()
            self.RequestedShipment.ShippingChargesPayment.PaymentType = 'COLLECT'
            Payor = self.factory.Payor()
            Payor.ResponsibleParty = self.factory.Party()
            Payor.ResponsibleParty.AccountNumber = self.picking.carrier_account
            self.RequestedShipment.ShippingChargesPayment.Payor = Payor
        elif self.picking.shipping_term in ['thirdparty']:
            self.RequestedShipment.ShippingChargesPayment = self.factory.Payment()
            self.RequestedShipment.ShippingChargesPayment.PaymentType = 'THIRD_PARTY'
            Payor = self.factory.Payor()
            Payor.ResponsibleParty = self.factory.Party()
            Payor.ResponsibleParty.AccountNumber = self.picking.carrier_account
            self.RequestedShipment.ShippingChargesPayment.Payor = Payor

FedexRequest.__init__ = __init__
FedexRequest.transaction_detail = transaction_detail
FedexRequest.shipping_charges_payment = shipping_charges_payment

class FedexRequestExtra(FedexRequest):

    def _add_package(self, weight_value, package_code=False, package_height=0, package_width=0, package_length=0, sequence_number=False, mode='shipping', po_number=False, dept_number=False, reference=False):
        package = self.factory.RequestedPackageLineItem()
        package_weight = self.factory.Weight()
        package_weight.Value = weight_value
        package_weight.Units = self.RequestedShipment.TotalWeight.Units

        package.PhysicalPackaging = 'BOX'
        if package_code == 'YOUR_PACKAGING':
            if self.picking.package_ids[sequence_number - 1] and self.picking.package_ids[sequence_number - 1].is_custom_dimensions:
                custom_package = self.picking.package_ids[sequence_number - 1]
                package_height = custom_package.height
                package_width = custom_package.width
                package_length = custom_package.packaging_length
            package.Dimensions = self.factory.Dimensions()
            package.Dimensions.Height = package_height
            package.Dimensions.Width = package_width
            package.Dimensions.Length = package_length
            # TODO in master, add unit in product packaging and perform unit conversion
            package.Dimensions.Units = "IN" if self.RequestedShipment.TotalWeight.Units == 'LB' else 'CM'
        if po_number:
            po_reference = self.factory.CustomerReference()
            po_reference.CustomerReferenceType = 'P_O_NUMBER'
            po_reference.Value = po_number
            package.CustomerReferences.append(po_reference)
        if dept_number:
            dept_reference = self.factory.CustomerReference()
            dept_reference.CustomerReferenceType = 'DEPARTMENT_NUMBER'
            dept_reference.Value = dept_number
            package.CustomerReferences.append(dept_reference)
        if reference:
            customer_reference = self.factory.CustomerReference()
            customer_reference.CustomerReferenceType = 'CUSTOMER_REFERENCE'
            customer_reference.Value = reference
            package.CustomerReferences.append(customer_reference)

        package.Weight = package_weight
        if mode == 'rating':
            package.GroupPackageCount = 1
        if sequence_number:
            package.SequenceNumber = sequence_number
        else:
            self.hasOnePackage = True

        if mode == 'rating':
            self.RequestedShipment.RequestedPackageLineItems.append(package)
        else:
            self.RequestedShipment.RequestedPackageLineItems = package

FedexRequest._add_package = FedexRequestExtra._add_package
#         
