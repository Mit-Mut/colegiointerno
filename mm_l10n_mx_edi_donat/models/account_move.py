from lxml.objectify import fromstring
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    donation = fields.Boolean("Donation", copy=False)
    is_generic_invoice = fields.Boolean("General Public Invoice", copy=False)
    vat_general_public_sale = fields.Char("General Public Sale Vat", copy=False)

    def _get_rfc(self, payment, customer):
        if payment.invoice_ids:
            invoice = payment.invoice_ids[0]
            if invoice.is_generic_invoice:
                return invoice.vat_general_public_sale
        return customer.l10n_mx_edi_get_customer_rfc()

    def action_post(self):
        for invoice in self:
            general_public_invoice = ''
            donation = ''
            counter = 0
            is_donation_in_prod = False
            for line in invoice.invoice_line_ids:
                if line.product_id:
                    if line.product_id.donation:
                        is_donation_in_prod = True
                    if counter == 0:
                        general_public_invoice = line.product_id.general_public_invoice
                        donation = line.product_id.donation
                    else:
                        if line.product_id.general_public_invoice != general_public_invoice:
                            raise UserError(
                                _("The invoice cannot be validated and stamped because it contains one or more items of different CFDI use (donations, services, products, etc.)"))
                        if line.product_id.donation != donation:
                            raise UserError(
                                _("The invoice cannot be validated and stamped because it contains one or more elements other than donations"))
                    counter += 1

            if is_donation_in_prod and not invoice.donation:
                raise UserError(_("Items in the bill are configured as donations, to stamp the bill must check \
                            the check box for donation on the bill"))
            if invoice.donation and not is_donation_in_prod:
                raise UserError(_("The products on the invoice are not configured as donations, in order to \
                            stamp the invoice you must uncheck the donation check box on the invoice or verify the \
                            configuration of the products"))

            if general_public_invoice:
                invoice.is_generic_invoice = True
                if not self.env.ref('mm_l10n_mx_edi_donat.generic_customer').vat:
                    raise UserError(_("Could not found VAT for 'General Public Sale'!"))
                invoice.vat_general_public_sale = self.env.ref('mm_l10n_mx_edi_donat.generic_customer').vat

        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()
        line_ids = self.mapped('line_ids').filtered(lambda line: line.sale_line_ids.is_downpayment)
        for line in line_ids:
            try:
                line.sale_line_ids.tax_id = line.tax_ids
                if all(line.tax_ids.mapped('price_include')):
                    line.sale_line_ids.price_unit = line.price_unit
                else:
                    #To keep positive amount on the sale order and to have the right price for the invoice
                    #We need the - before our untaxed_amount_to_invoice
                    line.sale_line_ids.price_unit = -line.sale_line_ids.untaxed_amount_to_invoice
            except UserError:
                # a UserError here means the SO was locked, which prevents changing the taxes
                # just ignore the error - this is a nice to have feature and should not be blocking
                pass
        return res
