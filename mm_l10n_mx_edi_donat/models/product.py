# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    general_public_invoice = fields.Boolean("General Public Invoice")
    donation = fields.Boolean("Donation")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    general_public_invoice = fields.Boolean("General Public Invoice")
    donation = fields.Boolean("Donation")

    