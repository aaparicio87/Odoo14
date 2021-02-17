from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    identification_id = fields.Many2one(
        comodel_name="l10n_cr.identification",
    )
    alias = fields.Char()
    condition = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
    )
    taxpayer = fields.Boolean()
    outstanding = fields.Monetary(string='Pendiente de Pago')
