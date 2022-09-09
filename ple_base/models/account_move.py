
from odoo import fields, models, api
import pytz
from datetime import datetime


class AccountMove(models.Model):

    _inherit = 'account.move'

    ple_state = fields.Selection(
        selection=[
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
        ],
        string='Estado PLE', default='1'
    )
    its_declared = fields.Boolean(
        string='Declarado?'
    )

    # origin_invoice_date = fields.Date(
    #     string='Fecha Rectificado'
    # )
    # !
    code_customs_id = fields.Many2one('code.customs', string='Code Customs')
    retention_id = fields.Many2one('account.retention', string='Retention')
    bool_pay_invoice = fields.Char(
        string='Indicador de comprobante de pago cancelado'
    )
    years = []

    for i in range(1981, datetime.today().year + 1):
        years.append(('{}'.format(i), '{}'.format(i)))

    year_aduana = fields.Selection(
        string='Año Emisión',
        selection=years,
        help='Año de emisión de la Declaración Aduanera de Mercancías - Importación '
             'definitiva o de la Despacho Simplificado - Importación Simplificada')
    voucher_number = fields.Char(string='Número de Pago')
    voucher_payment_date = fields.Date(string='Fecha pago')

    @api.model
    def _convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        date_tz = pytz.utc.localize(date_order).astimezone(tz)
        date_order = date_tz.strftime(format_time)
        return date_order

    @api.model_create_multi
    def create(self, values):
        invoice = super(AccountMove, self).create(values)
        invoice.update_correlative()
        return invoice

    def write(self, values):
        self.update_correlative()
        return super(AccountMove, self).write(values)

    def update_correlative(self):
        for invoice in self:
            prefix = invoice._get_type_contributo()
            i = 1
            for line in invoice.line_ids:
                line.correlative = '{}{}'.format(
                    prefix,
                    str(i).zfill(9)
                )
                i += 1

    def _get_type_contributo(self):
        self.ensure_one()
        new_name = self.journal_id.journal_correlative or ''
        return new_name
