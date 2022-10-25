from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
import datetime


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    _description = 'Res Currency Rate'

    # * Purchase

    purchase_rate = fields.Float('Purchase Rate', default=1, digits=0,
                                 group_operator="avg")
    company_purchase_rate = fields.Float(
        digits=0,
        compute="_compute_company_purchase_rate",
        inverse="_inverse_company_purchase_rate",
        group_operator="avg",
        help="The currency of purchase_rate 1 to the purchase_rate of the currency.",
    )
    inverse_company_purchase_rate = fields.Float(
        digits=0,
        compute="_compute_inverse_company_purchase_rate",
        inverse="_inverse_inverse_company_purchase_rate",
        group_operator="avg",
        help="The purchase_rate of the currency to the currency of purchase_rate 1 ",
    )

    _sql_constraints = [
        ('currency_purchase_rate_check', 'CHECK (purchase_rate>0)', 'The currency purchase rate must be strictly positive.'),
    ]

    @api.depends('company_purchase_rate')
    def _compute_inverse_company_purchase_rate(self):
        for currency_rate in self:
            currency_rate.inverse_company_purchase_rate = 1.0 / currency_rate.company_purchase_rate

    @api.onchange('inverse_company_purchase_rate')
    def _inverse_inverse_company_purchase_rate(self):
        for currency_rate in self:
            currency_rate.company_purchase_rate = 1.0 / currency_rate.inverse_company_purchase_rate

    @api.depends('purchase_rate', 'name', 'currency_id', 'company_id', 'currency_id.rate_ids.purchase_rate')
    @api.depends_context('company')
    def _compute_company_purchase_rate(self):
        last_rate = self.env['res.currency.rate']._get_last_purchase_rates_for_companies(self.company_id | self.env.company)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company
            currency_rate.company_purchase_rate = (currency_rate.purchase_rate or self._get_latest_purchase_rate().purchase_rate or 1.0) / last_rate[company]

    @api.onchange('company_purchase_rate')
    def _inverse_company_purchase_rate(self):
        last_rate = self.env['res.currency.rate']._get_last_purchase_rates_for_companies(self.company_id | self.env.company)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company
            currency_rate.purchase_rate = currency_rate.company_purchase_rate * last_rate[company]

    def _get_last_purchase_rates_for_companies(self, companies):
        return {
            company: company.currency_id.rate_ids.sudo().filtered(lambda x: (
                x.purchase_rate
                and x.company_id == company or not x.company_id
            )).sorted('name')[-1:].purchase_rate or 1
            for company in companies
        }

    def _get_latest_purchase_rate(self):
        # Make sure 'name' is defined when creating a new purchase_rate.
        if not self.name:
            raise UserError(_("The date for the current purchase_rate is empty.\nPlease set it."))
        return self.currency_id.rate_ids.sudo().filtered(lambda x: (
            x.purchase_rate
            and x.company_id == (self.company_id or self.env.company)
            and x.name < (self.name or fields.Date.today())
        )).sorted('name')[-1:]

    @api.depends('currency_id', 'company_id', 'name')
    def _compute_purchase_rate(self):
        for currency_rate in self:
            currency_rate.purchase_rate = currency_rate.purchase_rate or self._get_latest_purchase_rate().purchase_rate or 1.0

    @api.onchange('company_purchase_rate')
    def _onchange_purchase_rate_warning(self):
        latest_rate = self._get_latest_purchase_rate()
        if latest_rate:
            diff = (latest_rate.purchase_rate - self.purchase_rate) / latest_rate.purchase_rate
            if abs(diff) > 0.2:
                return {
                    'warning': {
                        'title': _("Warning for %s", self.currency_id.name),
                        'message': _(
                            "The new rate is quite far from the previous rate.\n"
                            "Incorrect currency rates may cause critical problems, make sure the rate is correct !"
                        )
                    }
                }

    # * Move

    @api.model
    def create(self, vals):
        res = super(ResCurrencyRate, self).create(vals)
        if 'rate' in vals:
            self._execute_compute_exchange_rate_moves(vals)
        return res

    def write(self, vals):
        res = super(ResCurrencyRate, self).write(vals)
        if 'rate' in vals:
            self._execute_compute_exchange_rate_moves(vals)
        return res

    def _execute_compute_exchange_rate_moves(self, vals):
        AccountMove = self.env['account.move']
        company = vals.get('company_id', self.company_id)
        currency = vals.get('currency_id', self.currency_id)
        date = vals.get('name', self.name)

        if type(date) == str:
            date_str = date
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date_str = date.strftime('%Y-%m-%d')
            date = date

        domain = [('date', '>=', date_str), ('company_id', '=', company.id), ('currency_id', '=', currency.id)]

        next_dates = currency.rate_ids.filtered(lambda cr: cr.name > date).sorted(lambda d: d.name)
        next_date = next_dates[0].name if next_dates else False

        if next_date:
            domain_extra = [('date', '<', next_date)]
            domain = expression.AND([domain, domain_extra])
        moves = AccountMove.search(domain)
        moves._get_exchange_rate()

    def _sanitize_vals(self, vals):
        vals = super(ResCurrencyRate, self)._sanitize_vals(vals)
        if 'inverse_company_purchase_rate' in vals and ('company_purchase_rate' in vals or 'purchase_rate' in vals):
            del vals['inverse_company_purchase_rate']
        if 'company_purchase_rate' in vals and 'purchase_rate' in vals:
            del vals['company_purchase_rate']
        return vals
