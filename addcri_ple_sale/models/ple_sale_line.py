from odoo import _, api, fields, models


class PleSaleLine(models.Model):
    _name = 'ple.sale.line'
    _description = 'ple.sale.line'

    row = fields.Integer('Fila')
    name = fields.Char(
        string='Periodo',
        required=True
    )
    ple_sale_id = fields.Many2one(
        comodel_name='ple.sale',
        string='Reporte de Venta'
    )
    number_origin = fields.Char(
        string=u'Número Origen'
    )
    journal_correlative = fields.Char(
        string='Correlativo Asiento'
    )
    date_invoice = fields.Date(string='Fecha de emisión')
    date = fields.Date(string='Fecha factura')
    date_due = fields.Date(
        string='Fecha de Vencimiento'
    )
    voucher_sunat_code = fields.Char(
        string='Tipo de Comprobante'
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Factura'
    )
    series = fields.Char(
        string='Series'
    )
    correlative = fields.Char(
        string='Correlativo Inicio'
    )
    correlative_end = fields.Char(
        string='Correlativo Fin'
    )
    customer_document_type = fields.Char(
        string='Tipo Doc. de Identidad'
    )
    customer_document_number = fields.Char(
        string='# Doc. de Identidad'
    )
    customer_name = fields.Char(
        string='Nombre Cliente'
    )
    amount_export = fields.Float(
        string='Valor Facturado de Exportación'
    )
    amount_untaxed = fields.Float(
        string='Operación Gravada'
    )
    discount_tax_base = fields.Float(
        string='Descuento de la base Imponible'
    )
    sale_no_gravadas_igv = fields.Float(
        string='Impuesto General a las Ventas y/o Impuesto de Promoción Municipal'
    )
    discount_igv = fields.Float(
        string='Descuento del Impuesto General a las Ventas'
    )
    amount_exonerated = fields.Float(
        string='Operación Exonerada'
    )
    amount_no_effect = fields.Float(
        string='Operación Inafecta'
    )
    isc = fields.Float(
        string='Impuesto Selectivo al Consumo'
    )
    rice_tax_base = fields.Float(
        string='Operación con IVA'
    )
    rice_igv = fields.Float(
        string='Impuesto de Operación con IVA'
    )
    another_taxes = fields.Float(
        string='Otros Conceptos, tributos y cargos'
    )
    amount_total = fields.Float(
        string='Total'
    )
    amount_taxed = fields.Float(string='Impuesto')
    code_currency = fields.Char(
        string='Código de la moneda'
    )
    currency_rate = fields.Float(
        string='Tipo de Cambio',
        digits=(12, 3)
    )
    origin_date_invoice = fields.Date(
        string='Fecha Pago'
    )
    origin_document_code = fields.Char(
        string='Tipo de comprobante'
    )
    origin_serie = fields.Char(
        string='Serie'
    )
    origin_correlative = fields.Char(
        string='Correlativo',
    )
    contract_name = fields.Char(
        string='Identificador de Contrato y/o Proyecto'
    )
    payment_voucher = fields.Integer(
        string='Identificador de comprobante de pago',
        default=1
    )
    inconsistency_type_change = fields.Char(
        string='Inconsistencia tipo de cambio'
    )
    ple_state = fields.Selection(
        selection=[
            ('1', '1'),
            ('2', '2'),
            ('8', '8'),
            ('9', '9'),
        ],
        string='Estado',
        default='1'
    )
    journal_name = fields.Char('Nombre de diario')
    document_code = fields.Char('Código de Documento')
    # tax_totals_json = fields.Char('Tax TOtals Json')
    ref = fields.Char('Referencia')
