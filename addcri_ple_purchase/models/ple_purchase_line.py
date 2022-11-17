from odoo import _, api, fields, models


class PlePurchaseLine(models.Model):

    _name = 'ple.purchase.line'
    _description = 'ple.purchase.line'

    row = fields.Integer('Fila')
    name = fields.Char(string='Periodo', required=True)
    ple_purchase_id = fields.Many2one('ple.purchase', string='Ple Purchase')
    invoice_id = fields.Many2one(comodel_name='account.move', string='Factura', required=True)
    number_origin = fields.Char(string='Número Origen')
    date_invoice = fields.Date(string='Fecha de emisión')
    date = fields.Date(string='Fecha factura')
    date_due = fields.Date(string='Fecha de Vencimiento')
    voucher_sunat_code = fields.Char(string='Tipo de Comprobante')
    series = fields.Char(string='Series')
    year_dua_dsi = fields.Char(string='Año Aduana')
    correlative = fields.Char(string='Correlativo')
    customer_document_type = fields.Char(string='Tipo Doc. de Identidad')
    customer_document_number = fields.Char(string='# Doc. de Identidad')
    customer_name = fields.Char(string='Nombre Cliente')
    base_gdg = fields.Float(string='Base GDG')
    tax_gdg = fields.Float(string='Impuesto GDG')
    base_gdm = fields.Float(string='Base GDM')
    tax_gdm = fields.Float(string='Impuesto GDM')
    base_gdng = fields.Float(string='Base GDNG')
    tax_gdng = fields.Float(string='Impuesto GDNG')
    amount_untaxed = fields.Float(string='Valor No Gravado')
    isc = fields.Float(string='Impuesto Selectivo al Consumo')
    another_taxes = fields.Float(string='Otros Conceptos, tributos y cargos')
    amount_total = fields.Float(string='Total')
    amount_taxed = fields.Float(string='Impuesto')
    code_currency = fields.Char(string='Código de la moneda')
    currency_rate = fields.Float(string='Tipo de Cambio', digits=(12, 3))
    origin_date_invoice = fields.Date(string='Fecha Pago')
    origin_document_code = fields.Char(string='Tipo de comprobante')
    origin_serie = fields.Char(string='Serie')
    origin_correlative = fields.Char(string='Correlativo de origen',)
    origin_code_aduana = fields.Char(string='Código aduana')
    journal_correlative = fields.Char(string='Correlativo Asiento')
    voucher_number = fields.Char(string='Número de Pago')
    voucher_date = fields.Date(string='Fecha de Pago')
    class_good_services = fields.Char(string='Clasifición Bienes/Servicios')
    irregular_societies = fields.Char(string='Sociedades Irregulares')
    error_exchange_rate = fields.Char(string='Error tipo de cambio')
    supplier_not_found = fields.Char(string='Proveedores no Habidos')
    suppliers_resigned = fields.Char(string='Proveedores que renunciarion')
    dni_ruc = fields.Char(string='DNI con RUC')
    type_pay_invoice = fields.Char(string='Indicador de comprobante de pago cancelado')
    ple_state = fields.Selection(selection=[('0', '0'),    ('1', '1'),    ('6', '6'),    ('7', '7'),    ('9', '9'), ], string='Estado PLE')
    country_code = fields.Char(string='Código del país de la residencia del sujeto no domiciliado')
    partner_street = fields.Char(string='Domicilio en el extranjero del sujeto no domiciliado')
    linkage_code = fields.Char(string='Vínculción', help="Consigna el Vínculo entre el contribuyente y el residente en el extranjero según los parámetros de la tabla 27 del Anexo N°3 Aprobado por R.S.N° 286-2009/SUNAT y modificatorias.")
    deduccion_cost = fields.Float(string='Deducción / Costo', digits=(12, 2))
    rent_neta = fields.Float(string='Renta Neta', digits=(12, 2))
    retention_rate = fields.Float(string='Tasa Retención', digits=(12, 2))
    tax_withheld = fields.Float(string='Impuesto retenido', digits=(12, 2),)
    cdi = fields.Char(string='CDI', help="Consigna Convenios para evitar la doble imposición según los parámetros de la tabla 25 del Anexo N°3 Aprobado por R.S.N° 286-2009/SUNAT y modificatorias. Si no hay convenio consignar 00")
    type_rent = fields.Char(string='Tipo de Renta', help="Consigna el tipo de Renta de la operación con el No domiciliado según los parámetros de la tabla 31 del Anexo N°3 Aprobado por R.S.N° 286-2009/SUNAT y modificatorias.")
    not_domiciled = fields.Boolean(string='No domiciliado')
    inv_type_document_code = fields.Char(string='Código de Tipo de Comprobante')
    inv_serie = fields.Char(string='Serie de Comprabante')
    inv_correlative = fields.Char(string='Correlativo de Comprobante')
    inv_year_dua_dsi = fields.Char(string='Año emisión  DUA o DSI')
    inv_retention_igv = fields.Float(string='Monto retención de IGV')
    hard_rent = fields.Float(string='Renta Bruta')
    exoneration_nodomicilied_code = fields.Char(string='Exoneración aplicada', help="Consigna la exoneración aplicada a No domiciliado según los parámetros de la tabla 33 del Anexo N°3 Aprobado por R.S.N° 286-2009/SUNAT y modificatorias.")
    type_rent_code = fields.Char(string='Código de tipo de Renta')
    taken_code = fields.Char(string='Modalidad de servicio prestado', help="Consigna la Modalidad del servicio prestado por el No domiciliado, según los parámetros de la tabla 32 del Anexo N°3 Aprobado por R.S.N° 286-2009/SUNAT y modificatorias.")
    application_article = fields.Char(string='Aplicación Art. 76°')
    retention = fields.Char(
        string='Retención'
    )
    ###
    journal_name = fields.Char('Nombre de diario')
    document_code = fields.Char('Código de Documento')
    ref = fields.Char('Referencia')

    # * me
    purchase_move_period = fields.Selection([
        ('0', 'Anotación optativa sin efecto en el IGV'),
        ('1', 'Fecha del documento corresponde al periodo en el que se anotó'),
        ('6', 'Fecha de emisión es anterior al periodo de anotación dentro de los 12 meses'),
        ('7', 'Fecha de emisión es anterior al periodo de anotación luego de los 12 meses'),
        ('9', 'Es ajuste o anotación')
    ], string='Estado de factura de compra')
    vat_inconsistent = fields.Boolean('DNI inconsistente')
    exchange_inconsistent = fields.Boolean('Inconsistencia en Tipo de cambio')
    cancel_with_payment_method = fields.Boolean('Cancelado con medio de pago')
    waived_exemption_from_igv = fields.Boolean('Renunció a exoneración de IGV')
    non_existing_supplier = fields.Boolean('Proveedor no habido')
    contract_or_project = fields.Char('Contrato o proyecto')
    adquisition_type = fields.Selection([
        ('1', 'Mercadería, materia prima, suministro, envases y embalajes'),
        ('2', 'Activo fijo'),
        ('3', 'Otros activos no considerados en los numerales 1 y 2'),
        ('4', 'Gastos de educación, recreación, salud, culturales, representación, capacitación, de viaje, mantenimiento de vehículos y de premios'),
        ('5', 'Otros gastos no incluidos en el numeral 4'),
    ], string='Tipo de adquisión')
    l10n_pe_dte_is_retention = fields.Boolean('Sujeto a retención')
    # * not domiciled
    not_domiciled_purchase_move_period = fields.Selection([
        ('0', 'Anotación optativa sin efecto en el IGV corresponde al periodo.'),
        ('9', 'Ajuste o rectificación en la anotación de la información de una operación registrada en un periodo anterior.')
    ], string='Estado de factura de compra no domiciliado')
