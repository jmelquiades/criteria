# -*- coding: utf-8 -*-

from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportXlsx(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'font_name': 'Arial'
        })

        ws = workbook.add_worksheet('Report de Venta')
        ws.set_column('A:A', 5)
        ws.set_column('B:B', 10)
        ws.set_column('C:C', 20)
        ws.set_column('D:D', 40)
        ws.set_column('E:E', 10)
        ws.set_column('F:F', 10)
        ws.set_column('G:G', 15)
        ws.set_column('H:H', 20)
        ws.set_column('I:I', 40)
        ws.set_column('J:J', 40)
        ws.set_column('K:K', 30)
        ws.set_column('L:L', 30)
        ws.set_column('M:M', 30)
        ws.set_column('N:N', 30)
        ws.set_column('N:N', 30)
        ws.set_column('O:O', 30)
        ws.set_column('P:P', 30)
        ws.set_column('Q:Q', 10)
        ws.set_column('R:R', 20)
        ws.set_column('S:S', 20)
        ws.set_column('T:T', 20)
        ws.set_column('V:V', 20)
        ws.set_column('X:X', 20)
        ws.set_column('Y:Y', 10)
        ws.set_column('AB:AB', 40)
        ws.set_column('AC:AC', 40)
        ws.set_column('AD:AD', 30)
        ws.set_column('AE:AE', 30)
        ws.set_column('AF:AF', 40)
        ws.set_column('AG:AG', 30)
        ws.set_column('AH:AH', 20)
        ws.set_column('AI:AI', 10)
        ws.set_column('AJ:AJ', 30)

        ws.set_row(0, 50)

        ws.write(0, 0, 'Fila', style1)
        ws.write(0, 1, 'Periodo', style1)
        ws.write(0, 2, 'Código Único de la \nOperación (CUO) o RER', style1)
        ws.write(0, 3, 'Número correlativo del \nasiento contable identificado en el campo 2', style1)
        ws.write(0, 4, 'F. emisión', style1)
        ws.write(0, 5, 'F. Vto. o Pago', style1)
        ws.write(0, 6, 'Tipo Comprobante', style1)
        ws.write(0, 7, 'Serie', style1)
        ws.write(0, 8, 'Número de comprobante, \no número inicial del consolidado diario', style1)
        ws.write(0, 9, 'Número de comprobante, \no número final del consolidado diario', style1)
        ws.write(0, 10, 'Tipo Documento Identidad', style1)
        ws.write(0, 11, 'Número Documento Identidad', style1)
        ws.write(0, 12, 'Apellidos y nombres, \ndenominación o razón social', style1)
        ws.write(0, 13, 'Valor facturado exportación', style1)
        ws.write(0, 14, 'Base imponible operación \ngravada', style1)
        ws.write(0, 15, 'Dscto. Base Imponible', style1)
        ws.write(0, 16, 'IGV y/o IPM', style1)
        ws.write(0, 17, 'Dscto. IGV y/o IPM', style1)
        ws.write(0, 18, 'Importe total operación \nexonerada', style1)
        ws.write(0, 19, 'Importe total operación \ninafecta', style1)
        ws.write(0, 20, 'ISC', style1)
        ws.write(0, 21, 'Base imponible IVAP', style1)
        ws.write(0, 22, 'IVAP', style1)
        ws.write(0, 23, 'Otros conceptos, \ntributos y cargos', style1)
        ws.write(0, 24, 'Importe total', style1)
        ws.write(0, 25, 'Moneda', style1)
        ws.write(0, 26, 'T.C.', style1)
        ws.write(0, 27, 'F. emisión documento original \nque se modifica', style1)
        ws.write(0, 28, 'Tipo comprobante que se modifica', style1)
        ws.write(0, 29, 'Serie comprobante de pago \nque se modifica', style1)
        ws.write(0, 30, 'Número comprobante de pago \nque se modifica', style1)
        ws.write(0, 31, 'Identificación del Contrato \nde colaboración que no \nlleva contabilidad independiente', style1)
        ws.write(0, 32, 'Error tipo 1: inconsistencia T.C.', style1)
        ws.write(0, 33, '¿Cancelado conmedio de pago?', style1)
        ws.write(0, 34, 'Estado PLE', style1)
        ws.write(0, 35, 'Campos de libre utilización', style1)

        i = 1
        for value in self.data:
            ws.write(i, 0, i)
            ws.write(i, 1, value['period'])
            ws.write(i, 2, value['number_origin'])
            ws.write(i, 3, value['journal_correlative'])
            ws.write(i, 4, value['date_invoice'])
            ws.write(i, 5, value['date_due'])
            ws.write(i, 6, value['voucher_sunat_code'])
            ws.write(i, 7, value['voucher_series'])
            ws.write(i, 8, value['correlative'])
            ws.write(i, 9, value['correlative_end'])
            ws.write(i, 10, value['customer_document_type'])
            ws.write(i, 11, value['customer_document_number'])
            ws.write(i, 12, value['customer_name'])
            ws.write(i, 13, value['amount_export'])
            ws.write(i, 14, value['amount_untaxed'])
            ws.write(i, 15, value['discount_tax_base'])
            ws.write(i, 16, value['sale_no_gravadas_igv'])
            ws.write(i, 17, value['discount_igv'])
            ws.write(i, 18, value['amount_exonerated'])
            ws.write(i, 19, value['amount_no_effect'])
            ws.write(i, 20, value['isc'])
            ws.write(i, 21, value['rice_tax_base'])
            ws.write(i, 22, value['rice_igv'])
            ws.write(i, 23, value['another_taxes'])
            ws.write(i, 24, value['amount_total'])
            ws.write(i, 25, value['code_currency'])
            ws.write(i, 26, value['currency_rate'])
            ws.write(i, 27, value['origin_date_invoice'])
            ws.write(i, 28, value['origin_document_code'])
            ws.write(i, 29, value['origin_serie'])
            ws.write(i, 30, value['origin_correlative'])
            ws.write(i, 31, value['contract_name'])
            ws.write(i, 32, value['inconsistency_type_change'])
            ws.write(i, 33, value['payment_voucher'])
            ws.write(i, 34, value['ple_state'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        name = self.obj.date_start.strftime('%Y%m')
        return 'Reporte_ventas_{}_{}.xlsx'.format(self.obj.company_id.name, name)
