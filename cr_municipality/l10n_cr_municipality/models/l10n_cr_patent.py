from odoo import _, api, fields, models
from odoo.tools import float_round
from odoo.exceptions import RedirectWarning, ValidationError


class Patent(models.Model):
    _inherit = "mail.thread"
    _name = "l10n_cr.patent"
    _description = "CR Patent"

    name = fields.Char(
        default=_("Solicitud"),
        readonly=True,
        string="Number",
        # TODO unique
        copy=False,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        default=lambda self: self.env.user,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    county_id = fields.Many2one(
        related="company_id.county_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("taxpayer", "=", True)],
        required=True,
    )
    solicitation_date = fields.Date(
        default=fields.Date.today,
    )
    type_id = fields.Many2one(
        required=True,
        comodel_name="l10n_cr.patent.type",
    )
    type_code = fields.Char(
        related="type_id.code",
    )
    fantasy_name = fields.Char()
    needs_liqueur = fields.Boolean(
        string="Requiere Patente Licor",
    )
    is_liqueur = fields.Boolean(
        compute="_compute_is_liqueur",
    )
    activity_ids = fields.Many2many(
        comodel_name="l10n_cr.ciiu",
    )
    commercial_activity = fields.Char()
    state = fields.Selection(
        string="Estado",
        selection=[
            ("requested", "Solicitada"),
            ("in_progress", "En Proceso"),
            ("approved", "Aprobada"),
            ("rejected", "Rechazada"),
            ("suspended", "Suspendida"),
            ("retired", "Retirada"),
            ("canceled", "Cancelada"),
        ],
        default="requested",
        required=True,
        tracking=True,
        copy=False,
    )
    land_id = fields.Many2one(
        required=True,
        comodel_name="l10n_cr.land",
    )
    address = fields.Char(
        related="land_id.address",
    )
    district_id = fields.Many2one(
        related="land_id.district_id",
    )
    plan_number = fields.Char(
        related="land_id.plan_number",
    )
    relation_type = fields.Selection(
        selection=[
            ("rented", "Rented"),
            ("loaned", "Loaned"),
            ("owned", "Owned"),
        ]
    )
    area = fields.Float()
    land_use_number = fields.Char()
    sanitary_permit = fields.Char()
    sanitary_permit_expiration = fields.Date()
    sanitary_permit_expiration = fields.Date()
    comply_7600 = fields.Boolean()
    income_total = fields.Monetary(
        string="Ingresos Brutos",
    )
    yearly_payment = fields.Monetary(
        string="Pago Anual",
        compute="_compute_yearly_payment",
        store=True,
        readonly=False,
    )
    trimester_payment = fields.Monetary(
        string="Pago Trimestral",
        compute="_compute_trimester_payment",
    )
    regimen = fields.Selection(
        string="Régimen",
        selection=[
            ("simplified", "Simplificado"),
            ("traditional", "Tradicional"),
        ],
    )
    category = fields.Selection(
        string="Categorías",
        selection=[
            ("commercial", "Comercial"),
            ("industrial", "Industrial"),
            ("services", "Servicios"),
            ("tourism", "Turismo"),
            ("agricultural", "Agropecuario"),
            ("entertainment", "Entretenimiento"),
            ("distribution", "Distribución"),
            ("financial", "Financiera"),
        ],
    )

    employees = fields.Integer(
        string="Cantidad de Empleados",
    )
    actives_value = fields.Monetary(
        string="Valor de los activos",
    )
    sales_value = fields.Monetary(
        string="Valor Ventas Netas",
    )
    score = fields.Float(
        string="Puntaje",
        compute="_compute_score",
    )
    category_liqueur = fields.Selection(
        string="Categoría",
        selection=[
            ("A", "Licorera (A)"),
            ("B1", "Bar (B1)"),
            ("B2", "Bar c/ actividad bailable (B2)"),
            ("C", "Restaurant (C)"),
            ("D1", "Minisúoer (D1)"),
            ("D2", "Supermercado (D2)"),
            ("E1A", "Hospedaje <15 (E1A)"),
            ("E1B", "Hospedaje >15 (E1B)"),
            ("E2", "Marinas (E2)"),
            ("E3", "Gastronómicas (E3)"),
            ("E4", "Centros nocturnos (E4)"),
            ("E5", "Actividades temáticas (E5)"),
        ],
    )
    subcategory_liqueur = fields.Selection(
        string="Subcategoría",
        selection=[
            ("A1", "A1"),
            ("A2", "A2"),
            ("A3", "A3"),
            ("A4", "A4"),
        ],
    )

    liqueur_patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        string="Patente de Licor",
        readonly=True,
    )
    employees_rel = fields.Integer(
        related="liqueur_patent_id.employees",
        readonly=False,
    )
    actives_value_rel = fields.Monetary(
        related="liqueur_patent_id.actives_value",
        readonly=False,
    )
    sales_value_rel = fields.Monetary(
        related="liqueur_patent_id.sales_value",
        readonly=False,
    )
    yearly_payment_rel = fields.Monetary(
        # related="liqueur_patent_id.yearly_payment",
        compute="_compute_yearly_payment_rel",
        store=True,
    )
    trimester_payment_rel = fields.Monetary(
        string="Pago Trimestral",
    )
    category_liqueur_rel = fields.Selection(
        related="liqueur_patent_id.category_liqueur",
        readonly=False,
    )
    subcategory_liqueur_rel = fields.Selection(
        related="liqueur_patent_id.subcategory_liqueur",
        readonly=False,
    )

    timbre = fields.Monetary(
        compute="_compute_timbre",
    )
    yearly_payment_subtotal = fields.Monetary(
        string="Pago Anual",
        compute="_compute_payment_total",
    )
    yearly_payment_total = fields.Monetary(
        string="Pago Anual con Timbre",
        compute="_compute_payment_total",
    )
    trimester_payment_total = fields.Monetary(
        string="Pago Trimestral",
        compute="_compute_trimester_payment",
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True,
    )

    liqueur_open_hour = fields.Float(
        string='Hora de Apertura',
        compute="_compute_liqueur_open_hour",
        store=True,
        readonly=False,
    )

    liqueur_close_hour = fields.Float(
        string='Hora de Cierre',
        compute="_compute_liqueur_close_hour",
        store=True,
        readonly=False,
    )
    liqueur_open_hour_rel = fields.Float(
        related="liqueur_patent_id.liqueur_open_hour",
        readonly=False,
    )

    liqueur_close_hour_rel = fields.Float(
        related="liqueur_patent_id.liqueur_close_hour",
        readonly=False,
    )
    req_deliver_id = fields.Many2many(
        'l10n_cr.req_deliver', column1='patent_id', column2='req_deliver_id',
        string='Deliver Requirements'
    )
    req_miss_id = fields.Many2many(
        'l10n_cr.req_miss', column1='patent_id',
        column2='req_miss_id', string='Miss Requirements'
    )
    reject_motive = fields.Text(
        string='Reject Motive',
    )
    resolution_date = fields.Date(
        string='Resolution Date'
    )
    property_owner = fields.Char(
        related="land_id.partner_id.name",
        string='Popietario',
        readonly=True
    )
    pay_to = fields.Date(
        string='Pagado A',
        readonly=True
    )
    def create_liqueur_patent(self, vals):
        self.liqueur_patent_id = self.copy(
            {
                "name": _("New"),
                "type_id": self.env.ref("l10n_cr_municipality.patent_type_liquors").id,
                "needs_liqueur": False,
                "employees": vals.get("employees_rel"),
                "actives_value": vals.get("actives_value_rel"),
                "sales_value": vals.get("sales_value_rel"),
                "yearly_payment": vals.get("yearly_payment_rel"),
            }
        )

    def write(self, vals):
        res = super(Patent, self).write(vals)
        if vals.get("needs_liqueur"):
            self.create_liqueur_patent(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(Patent, self).create(vals)

        patent_type = res.type_id
        sequence = patent_type.sequence_id
        district = res.land_id.district_id
        res.name = (
            f"{patent_type.code}-{district.code}-{sequence.next_by_id()}"  # TODO district.code
        )
        if res.needs_liqueur:
            res.create_liqueur_patent(vals)

        return res

    def get_payment_simplified(self):
        base_salary = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.base_salary"))
        scales = [
            (0, 13 / 100 * base_salary),
            (25000000, 20 / 100 * base_salary),
            (50000000, 25 / 100 * base_salary),
            (65000000, 30 / 100 * base_salary),
        ]
        payment = 0
        for scale in scales:
            if self.income_total < scale[0]:
                break
            payment = scale[1]
        return payment

    @api.depends("regimen", "income_total")
    def _compute_yearly_payment(self):
        for patent in self:
            if patent.regimen == "traditional":
                patent.yearly_payment = patent.income_total * (1.5 / 1000)
            elif patent.regimen == "simplified":
                patent.yearly_payment = self.get_payment_simplified()
            else:
                patent.yearly_payment = 0
            if patent.type_id.code == "EM":
                base_salary = float(
                    self.env["ir.config_parameter"].sudo().get_param("l10n_cr.base_salary")
                )
                patent.yearly_payment = (10 / 100) * base_salary

    @api.depends("yearly_payment", "yearly_payment_total")
    def _compute_trimester_payment(self):
        for patent in self:
            patent.trimester_payment = patent.yearly_payment / 4
            patent.trimester_payment_total = patent.yearly_payment_total / 4

    @api.depends(
        "employees",
        "actives_value",
        "sales_value",
        "employees_rel",
        "actives_value_rel",
        "sales_value_rel",
    )
    def _compute_score(self):
        ntcs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.ntcs"))
        vncs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.vncs"))
        atcs = float(self.env["ir.config_parameter"].sudo().get_param("l10n_cr.atcs"))

        if ntcs and vncs and atcs > 0:
            for patent in self:
                patent.score = (
                    0.6 * (patent.employees or patent.employees_rel) / ntcs
                    + 0.3 * (patent.actives_value or patent.actives_value_rel) / vncs
                    + 0.1 * (patent.sales_value or patent.sales_value_rel) / atcs
                ) * 100
        else:
            raise ValidationError(_('Check the values ​​of the NTcs, VNcs and ATcs fields that cannot be empty.\n'
                                    'Go to Settings / Municipality.'))
            

    @api.depends("yearly_payment_liqueur")
    def _compute_trimester_payment_liqueur(self):
        for patent in self:
            patent.trimester_payment_liqueur = patent.yearly_payment_liqueur / 4

    @api.depends(
        "yearly_payment", "yearly_payment_rel", "trimester_payment", "trimester_payment_rel"
    )
    def _compute_payment_total(self):
        for patent in self:
            patent.yearly_payment_subtotal = patent.yearly_payment + patent.yearly_payment_rel
            patent.yearly_payment_total = patent.yearly_payment_subtotal + patent.timbre

    @api.depends("type_id")
    def _compute_is_liqueur(self):
        for patent in self:
            patent.is_liqueur = patent.type_code == "LC"

    @api.depends("type_id", "yearly_payment_subtotal")
    def _compute_timbre(self):
        for patent in self:
            patent.timbre = patent.yearly_payment_subtotal * (2 / 100)

    @api.depends("trimester_payment_rel")
    def _compute_yearly_payment_rel(self):
        for patent in self:
            patent.yearly_payment_rel = patent.trimester_payment_rel * 4
            if patent.liqueur_patent_id:
                patent.liqueur_patent_id.yearly_payment = patent.yearly_payment_rel

    def action_view_invoices(self):  # TODO REM
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action["domain"] = [
            ("patent_id", "=", self.id),
        ]
        return action
    
    @api.depends(
        'category_liqueur', 'category_liqueur_rel'
    )
    def _compute_liqueur_open_hour(self):
        for patent in self:
            if patent.category_liqueur == 'A' or patent.category_liqueur == 'B1':
                o_temp = '11'
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == 'A' or patent.category_liqueur_rel == 'B1':
                o_temp = '11'
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == 'B2':
                o_temp = '16'
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == 'B2':
                o_temp = '16'
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == 'C':
                o_temp = '11'
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == 'C':
                o_temp = '11'
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == 'D1' or patent.category_liqueur == 'D2':
                o_temp = '8'
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == 'D1' or patent.category_liqueur_rel == 'D2':
                o_temp = '8'
                patent.liqueur_open_hour_rel = float(o_temp)

            if patent.category_liqueur == 'E1A' or patent.category_liqueur == 'E1B' or patent.category_liqueur == 'E2' or patent.category_liqueur == 'E3' or patent.category_liqueur == 'E4' or patent.category_liqueur == 'E5':
                o_temp = '00'
                patent.liqueur_open_hour = float(o_temp)
            if patent.category_liqueur_rel == 'E1A' or patent.category_liqueur_rel == 'E1B' or patent.category_liqueur_rel == 'E2' or patent.category_liqueur_rel == 'E3' or patent.category_liqueur_rel == 'E4' or patent.category_liqueur_rel == 'E5':
                o_temp = '00'
                patent.liqueur_open_hour_rel = float(o_temp)

    @api.depends(
        'category_liqueur', 'category_liqueur_rel'
    )
    def _compute_liqueur_close_hour(self):
        for patent in self:
            if patent.category_liqueur == 'A' or patent.category_liqueur == 'B1':
                c_temp = '00'
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == 'A' or patent.category_liqueur_rel == 'B1':
                c_temp = '00'
                patent.liqueur_close_hour_rel = float(c_temp)

            if patent.category_liqueur == 'B2':
                c_temp = '2.5'
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == 'B2':
                c_temp = '2.5'
                patent.liqueur_close_hour_rel = float(c_temp)
            if patent.category_liqueur == 'C':
                c_temp = '2.5'
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == 'C':
                c_temp = '2.5'
                patent.liqueur_close_hour_rel = float(c_temp)

            if patent.category_liqueur == 'D1' or patent.category_liqueur == 'D2':
                c_temp = '00'
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == 'D1' or patent.category_liqueur_rel == 'D2':
                c_temp = '00'
                patent.liqueur_close_hour_rel = float(c_temp)

            if patent.category_liqueur == 'E1A' or patent.category_liqueur == 'E1B' or patent.category_liqueur == 'E2' or patent.category_liqueur == 'E3' or patent.category_liqueur == 'E4' or patent.category_liqueur == 'E5':
                c_temp = '00'
                patent.liqueur_close_hour = float(c_temp)
            if patent.category_liqueur_rel == 'E1A' or patent.category_liqueur_rel == 'E1B' or patent.category_liqueur_rel == 'E2' or patent.category_liqueur_rel == 'E3' or patent.category_liqueur_rel == 'E4' or patent.category_liqueur_rel == 'E5':
                c_temp = '00'
                patent.liqueur_close_hour_rel = float(c_temp)


    def process(self):
        self.ensure_one()
        self.state = 'in_progress'

    def approve(self):
        self.ensure_one()
        # TODO permissions
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent.approve_wizard",
            "target": "new",
        }

    def reject(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent.reject_wizard",
            "target": "new",
        }

    def print_approve(self):
        self.ensure_one()
        if self.state == 'approved':
            if self.type_id.name == 'Licores':
                return self.env.ref('l10n_cr_municipality.report_patent_aprob_licor').report_action(self)
            else:
                return self.env.ref('l10n_cr_municipality.report_patent_aprob_mcr').report_action(self)

    def print_reject(self):
        self.ensure_one()
        if self.state == 'rejected':
            if self.type_id.name == 'Licores':
                return self.env.ref('l10n_cr_municipality.report_patent_deneg_licor').report_action(self)
            else:
                return self.env.ref('l10n_cr_municipality.report_patent_deneg_mcr').report_action(self)

    def print_cert(self):
        self.ensure_one()
        if self.state == 'approved':
            return self.env.ref('l10n_cr_municipality.patent_certificate').report_action(self)

    def action_view_sale(self):
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order",
            "res_id": self.sale_id.id,
            "target": "current",
        }
