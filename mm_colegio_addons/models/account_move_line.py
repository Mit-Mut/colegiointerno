from odoo import _, models, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_id = fields.Many2one('account.move', string='Invoice Reference',
        ondelete='cascade', index=True)
