from odoo import _, api, fields, models
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class PleBase(models.Model):
    _name = 'ple.base'
    _description = 'ple.base'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.depends('period_year', 'period_month')
    def _get_date(self):
        month = int(self.period_month)
        year = int(self.period_year)
        date_reference = date(year, month, 1)
        self.date_start = date_reference
        self.date_end = date_reference + relativedelta(months=1) - timedelta(days=1)

    name = fields.Char('Name')
    date_start = fields.Date('Fecha Inicio', required=True, compute=_get_date)
    date_end = fields.Date('Fecha Fin', required=True, compute=_get_date)
    state = fields.Selection(selection=[
        ('draft', 'No declarado'),
        ('closed', 'Declarado')
    ], string='Estado', default='draft', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    datetime_ple = fields.Datetime('Fecha de generación de reporte PLE')
    line_ids = fields.One2many('ple.base.line', 'ple_base_id', string='Ple Base Line')

    period_month = fields.Selection(selection=[('1', 'Ene'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Abr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Ago'), ('9', 'Set'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dic')],  required=True)  # default='1',

    period_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range((fields.Datetime.now().year) - 2, (fields.Datetime.now().year) + 5))], string="Period", required=True)  # , default=str(fields.Datetime.now().year)

    _sql_constraints = [
        ("year_month_unique", "unique(period_year, period_month, company_id)", "El periodo debe de ser único por compañía."),
    ]

    def _get_name(self, vals):
        # date_start = vals.get('date_start', self.date_start)
        # date_end = vals.get('date_end', self.date_end)
        year = vals.get('period_year', self.period_year)
        month = vals.get('period_month', self.period_month).zfill(2) if vals.get('period_month', self.period_month) else False
        # company_id = vals.get('company_id', self.company_id.id)
        # company = self.env['res.company'].browse(company_id).name
        return str(year) + str(month)  # + ' ' + company

    def default_get(self, fields_list):
        res = super(PleBase, self).default_get(fields_list)
        date = fields.date.today()
        period_year = str(date.year)
        period_month = str(date.month)
        res.update({
            'period_year': period_year,
            'period_month': period_month
        })
        return res

    def write(self, vals):
        vals['name'] = self._get_name(vals)
        return super(PleBase, self).write(vals)

    @api.onchange('period_year', 'period_month', 'company_id')
    def _onchange_date_company(self):
        self.line_ids.unlink()

    def delete_old_record(self, search_model='ple.sale.purchase', model=False):
        record_old = self.env[search_model].search([
            ('period_year', '=', self.period_year),
            ('period_month', '=', self.period_month),
            ('company_id', '=', self.company_id.id)
        ])
        if record_old:
            if (model == 'ple.sale' and not record_old.ple_purchase_id) or (model == 'ple.purchase' and not record_old.ple_sale_id):
                record_old.ple_purchase_id = False
                record_old.ple_sale_id = False
                record_old.unlink()

    def create_report(self, vals, search_model='ple.sale.purchase', model=False):
        self.delete_old_record(search_model, model)

        #################################
        if search_model:
            record = self.env[search_model].search([
                ('period_year', '=', vals.get('period_year', self.period_year)),
                ('period_month', '=', vals.get('period_month', self.period_month)),
                ('company_id', '=', vals.get('company_id', self.company_id.id))
            ])
            if record:
                if model == 'ple.sale':
                    record.ple_sale_id = self.id
                elif model == 'ple.purchase':
                    record.ple_purchase_id = self.id
            else:
                data = {
                    'period_year': vals.get('period_year', self.period_year),
                    'period_month': vals.get('period_month', self.period_month),
                    'company_id': vals.get('company_id', self.company_id.id)
                }
                if model == 'ple.sale':
                    data.update(ple_sale_id=self.id)
                elif model == 'ple.purchase':
                    data.update(ple_purchase_id=self.id)
                self.env[search_model].create(data)

    @api.model
    def create(self, vals):
        vals['name'] = self._get_name(vals)
        return super(PleBase, self).create(vals)

    def _get_number_origin(self, invoice):
        number_origin = ''
        try:
            if invoice.type in ['out_invoice', 'out_refund']:
                if invoice.ple_state in ['0', '1', '2', '8', '9']:
                    number_origin = invoice.name.replace('/', '').replace('-', '')

            elif invoice.type in ['in_invoice', 'in_refund']:
                if invoice.ple_state in ['0', '1', '6', '7', '9']:
                    number_origin = invoice.name.replace('/', '').replace('-', '')

        except Exception:
            number_origin = ''
        return number_origin

    def _get_data_invoice(self, invoice):  # *
        ple_state = invoice.ple_state
        partner = invoice.partner_id
        if invoice.state != 'cancel':
            return invoice.invoice_date_due, ple_state, partner.l10n_latam_identification_type_id.l10n_pe_vat_code, partner.vat, partner.name  # ! partner.l10n_latam_identification_type_id.sequence >> partner.l10n_latam_identification_type_id.code
        else:
            return False, ple_state, partner.l10n_latam_identification_type_id.l10n_pe_vat_code, partner.vat, partner.name

    def _get_journal_correlative(self, company, invoice=False, new_name=''):
        if company.type_contributor == 'CUO':

            if not new_name:
                new_name = 'M000000001'
        elif company.type_contributor == 'RER':
            new_name = 'M-RER'
        return new_name

    def _get_data_origin(self, invoice):  # * corregido
        # ! return invoice.origin_invoice_date, invoice.origin_inv_document_type_id.code, invoice.origin_serie, invoice.origin_correlative, invoice.origin_number.code_aduana
        # l10n_pe_dte_rectification_ref_type
        return invoice.reversed_entry_id.invoice_date, invoice.reversed_entry_id.l10n_latam_document_type_id.code, invoice.reversed_entry_id.sequence_prefix.split()[-1].replace('-', '') if type(invoice.reversed_entry_id.sequence_prefix) == str else '', invoice.reversed_entry_id.sequence_number, invoice.reversed_entry_id.code_customs_id

    def unlink(self):
        for record in self:
            if record.state == 'closed':
                raise UserError('Regrese a estado borrador para revertir y permitir eliminar.')
            return super(PleBase, self).unlink()

    def _refund_amount(self, values):
        for k in values.keys():
            values[k] *= -1
        return values

    def action_close(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError('No hay registros para declarar.')
        for obj_line in self.line_ids:
            if obj_line.invoice_id:
                obj_line.invoice_id.its_declared = True
        self.write({
            'state': 'closed'
        })
        return True

    def action_rollback(self):
        for obj_line in self.line_ids:
            if obj_line.invoice_id:
                obj_line.invoice_id.its_declared = False
        self.state = 'draft'
        return True
