
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

    # * ple ventas

    sale_move_period = fields.Selection([
        ('0', 'Anotación sin efecto en el IGV'),
        ('1', 'Fecha del comprobante corresponde al periodo'),
        ('2', 'Documento anulado'),
        ('8', 'Corresponde al periodo anterior'),
        ('9', 'Se está corrigiendo una anotación de periodo anterior')
    ], string='Estado de factura de venta', default="1")

    exchange_inconsistent = fields.Boolean('Inconsistencia en Tipo de cambio')
    cancel_with_payment_method = fields.Boolean('Cancelado con medio de pago')
    contract_number = fields.Char('Número de contrato')
    latest_consolidated_number = fields.Char('Último número consolidado')

    # * ple comroas

    initial_consolidated_number = fields.Char('Nùmero inicial consolidado')
    adquisition_type = fields.Selection([
        ('1', 'Mercadería, materia prima, suministro, envases y embalajes'),
        ('2', 'Activo fijo'),
        ('3', 'Otros activos no considerados en los numerales 1 y 2'),
        ('4', 'Gastos de educación, recreación, salud, culturales, representación, capacitación, de viaje, mantenimiento de vehículos y de premios'),
        ('5', 'Otros gastos no incluidos en el numeral 4'),
    ], string='Tipo de adquisión', default='1')
    contract_or_project = fields.Char('Contrato o proyecto')
    non_existing_supplier = fields.Boolean('Proveedor no habido')
    waived_exemption_from_igv = fields.Boolean('Renunció a exoneración de IGV')
    vat_inconsistent = fields.Boolean('DNI inconsistente')
    purchase_clearance = fields.Boolean('Liquidación de compra')
    purchase_move_period = fields.Selection([
        ('0', 'Anotación optativa sin efecto en el IGV'),
        ('1', 'Fecha del documento corresponde al periodo en el que se anotó'),
        ('6', 'Fecha de emisión es anterior al periodo de anotación dentro de los 12 meses'),
        ('7', 'Fecha de emisión es anterior al periodo de anotación luego de los 12 meses'),
        ('9', 'Es ajuste o anotación')
    ], string='Estado de factura de compra', default='1')
    purchase_ple_modification_date = fields.Datetime('Fecha de modificación de PLE de compras')

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
