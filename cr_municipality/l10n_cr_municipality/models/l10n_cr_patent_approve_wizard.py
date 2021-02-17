from datetime import date

from odoo import _, fields, models
from odoo.tools import date_utils

class PatentApproveWizard(models.TransientModel):
    _name = "l10n_cr.patent.approve_wizard"
    _description = "CR Patent Invoice Wizard"

    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        required=True,
        default=lambda self: self.env["l10n_cr.patent"].browse(self._context["active_id"]),
        readonly=True,
    )
    full_year = fields.Boolean(
        string="Año completo",
    )
    apply_discount = fields.Boolean(
        string="Aplicar Descuento",
    )

    def _get_trimesters(self):  # TODO create timesters based on count
        months = int(12 / (1 if self.full_year else 4))
        discount = float(
            self.env["ir.config_parameter"].sudo().get_param("l10n_cr.payment_in_advance_discount")
        )
        patent_name = self.patent_id.name
        trimesters = [
            {
                "name": _(f"Patente {patent_name} trimestre {t+1:02d}-{t+3:02d}"),
                "discount": discount if self.apply_discount else 0,
                "account_id": self.patent_id.company_id.advance_account_id.id if t > 0 else [],
                "advance": t > 0,
            }
            for t in range(0, months, 3)
        ]
        return trimesters

    def _get_trimester_percentage_left(self):
        first_day = date(2021, 1, 1)
        last_day = date(2021, 3, 31)
        total_day = (last_day - first_day).days
        days_to_end = (last_day - fields.Date.today()).days
        return days_to_end / total_day

    def _get_sale_lines(self):
        trimesters = self._get_trimesters()
        types = [
            (self.patent_id.type_id, self.patent_id.trimester_payment),
        ]
        if self.patent_id.liqueur_patent_id:
            types.append(
                (self.patent_id.liqueur_patent_id.type_id, self.patent_id.trimester_payment_rel)
            )
        trimester_percentage_left = self._get_trimester_percentage_left()
        lines = [
            {  # TODO compute
                "product_id": (
                    patent_type[0].product_advance_id
                    if trimester["advance"]
                    else patent_type[0].product_id
                ).id,
                "name": trimester["name"],
                "price_unit": patent_type[1]
                * (1 if trimester["advance"] else trimester_percentage_left),
                "discount": trimester["discount"],
            }
            for patent_type in types
            for trimester in trimesters
        ]
        timbre_percentage = len(trimesters) / 4
        lines.append(
            {
                "product_id": self.env.ref("l10n_cr_municipality.product_timbre").id,
                "price_unit": self.patent_id.timbre * timbre_percentage,
            }
        )
        return [(0, None, line) for line in lines]

    def create_sale(self):
        lines = self._get_sale_lines()
        sale_data = {
            "partner_id": self.patent_id.partner_id.id,
            "patent_id": self.patent_id.id,
            "order_line": lines,
        }
        sale = self.env["sale.order"].create(sale_data)
        return sale

    def get_pay_to(self, today):
        last_day = last = date(today.year, 12, 31)
        trim = date_utils.get_quarter(today)
        if self.full_year:
            return last_day

        return trim[1]

    def approve(self):
        today = fields.Date.today()
        pay_to = self.get_pay_to(today)

        for wizard in self:
            wizard.patent_id.sale_id = wizard.create_sale()
            wizard.patent_id.sale_id.action_confirm()
            invoices = wizard.patent_id.sale_id._create_invoices()
            invoices.action_post()
            invoices.patent_id = wizard.patent_id
            wizard.patent_id.state = "approved"
            wizard.patent_id.resolution_date = fields.Date.today()
            wizard.patent_id.pay_to = pay_to
            if len(self) == 1:
                return wizard.patent_id.sale_id.action_view_invoice()
        return {}
