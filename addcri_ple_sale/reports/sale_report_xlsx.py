# -*- coding: utf-8 -*-

from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class SaleReportXlsx(object):

    def __init__(self, obj, data):
        self.obj = obj
        # self.data = data
        self.data_14_1, self.data_14_2 = data

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
        for value in self.data_14_1:
            ws.write(i, 0, i)
            ws.write(i + i, 0, i + 1)
            ws.write(i + i, 1, value['field_1'])
            ws.write(i + i, 2, value['field_2'])
            ws.write(i + i, 3, value['field_3'])
            ws.write(i + i, 4, value['field_4'])
            ws.write(i + i, 5, value['field_5'])
            ws.write(i + i, 6, value['field_6'])
            ws.write(i + i, 7, value['field_7'])
            ws.write(i + i, 8, value['field_8'])
            ws.write(i + i, 9, value['field_9'])
            ws.write(i + i, 10, value['field_10'])
            ws.write(i + i, 11, value['field_11'])
            ws.write(i + i, 12, value['field_12'])
            ws.write(i + i, 13, value['field_13'])
            ws.write(i + i, 14, value['field_14'])
            ws.write(i + i, 15, value['field_15'])
            ws.write(i + i, 16, value['field_16'])
            ws.write(i + i, 17, value['field_17'])
            ws.write(i + i, 18, value['field_18'])
            ws.write(i + i, 19, value['field_19'])
            ws.write(i + i, 20, value['field_20'])
            ws.write(i + i, 21, value['field_21'])
            ws.write(i + i, 22, value['field_22'])
            ws.write(i + i, 23, value['field_23'])
            ws.write(i + i, 24, value['field_24'])
            ws.write(i + i, 25, value['field_25'])
            ws.write(i + i, 26, value['field_26'])
            ws.write(i + i, 27, value['field_27'])
            ws.write(i + i, 28, value['field_28'])
            ws.write(i + i, 29, value['field_29'])
            ws.write(i + i, 30, value['field_30'])
            ws.write(i + i, 31, value['field_31'])
            ws.write(i + i, 32, value['field_32'])
            ws.write(i + i, 33, value['field_33'])
            ws.write(i + i, 34, value['field_34'])
            ws.write(i + i, 35, value['field_35'])
            ws.write(i + i, 36, value['field_36'])
            i += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, month, year, company):
        return f'RV_{year}_{month}_{company}.xlsx'
