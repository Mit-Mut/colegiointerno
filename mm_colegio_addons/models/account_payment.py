from odoo import _, models, api
from odoo.tools.misc import formatLang, format_date


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def change_amt_in_word(self):
        for record in self:
            record.check_amount_in_words = record.currency_id.amount_to_text(record.amount) if record.currency_id else False
