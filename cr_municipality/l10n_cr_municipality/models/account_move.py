from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        readonly=True,
    )
