# -*- coding: utf-8 -*-

from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class PurchaseReportXlsx(object):

    def __init__(self, obj, data):
        self.obj = obj
        # self.data = data
        self.data_8_1, self.data_8_2 = data

    def _get_content_8_1(self, ws, style_header, style_column, style_number, style_number_bold, style_content, style_date):
        ws.set_column(0, 0, 4)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 14)
        ws.set_column(3, 3, 12)
        ws.set_column(4, 4, 10)
        ws.set_column(5, 5, 10)
        ws.set_column(6, 6, 4)
        ws.set_column(7, 7, 6)
        ws.set_column(8, 8, 8)
        ws.set_column(9, 9, 12)
        ws.set_column(10, 10, 12)
        ws.set_column(11, 11, 4)
        ws.set_column(12, 12, 12)
        ws.set_column(13, 13, 20)
        ws.set_column(14, 14, 17)
        ws.set_column(15, 15, 14)
        ws.set_column(16, 16, 17)
        ws.set_column(17, 17, 14)
        ws.set_column(18, 18, 17)
        ws.set_column(19, 19, 14)
        ws.set_column(20, 20, 17)
        ws.set_column(21, 21, 14)
        ws.set_column(22, 22, 14)
        ws.set_column(23, 23, 17)
        ws.set_column(24, 24, 5)
        ws.set_column(25, 25, 6)
        ws.set_column(26, 26, 10)
        ws.set_column(27, 27, 4)
        ws.set_column(28, 28, 6)
        ws.set_column(29, 29, 8)
        ws.set_column(30, 30, 12)
        ws.set_column(31, 31, 10)
        ws.set_column(32, 32, 14)
        ws.set_column(33, 33, 3)
        ws.set_column(34, 34, 6)
        ws.set_column(35, 35, 8)
        ws.set_column(36, 36, 3)
        ws.set_column(37, 37, 3)
        ws.set_column(38, 38, 3)
        ws.set_column(39, 39, 3)
        ws.set_column(40, 40, 3)
        ws.set_column(41, 41, 3)
        ws.set_column(42, 42, 3)

        header = 0
        total = header + 3
        row_c = total + 1
        row_i = row_c + 1

        ws.write(header, 0, 'Registro de Compras Formato 8.1 de la empresa {}'.format(
            self.obj.company_id.name
        ), style_header)
        ws.write(header + 1, 0, 'Por el periodo comprendio desde el {} al {}'.format(
            self.obj.date_start.strftime('%d/%m/%Y'),
            self.obj.date_end.strftime('%d/%m/%Y')
        ), style_header)

        ws.write(row_c, 0, 'Fila', style_column)
        ws.write(row_c, 1, 'Periodo', style_column)
        ws.write(row_c, 2, 'CUO', style_column)
        ws.write(row_c, 3, 'Correlativo', style_column)
        ws.write(row_c, 4, 'F. Emisión', style_column)
        ws.write(row_c, 5, 'F. V.', style_column)
        ws.write(row_c, 6, 'Tipo Doc.', style_column)
        ws.write(row_c, 7, 'Serie', style_column)
        ws.write(row_c, 8, 'Año DUA', style_column)
        ws.write(row_c, 9, 'Correlativo', style_column)
        ws.write(row_c, 10, 'Número Final', style_column)
        ws.write(row_c, 11, 'T. Doc.', style_column)
        ws.write(row_c, 12, 'N° Doc.', style_column)
        ws.write(row_c, 13, 'Nombre o Razón Social', style_column)
        ws.write(row_c, 14, 'BI Op. Gvds. dest. a op. Grvds.', style_column)
        ws.write(row_c, 15, 'IGV', style_column)
        ws.write(row_c, 16, 'BI Op. Gvds. dest. a op. Mixta', style_column)
        ws.write(row_c, 17, 'IGV', style_column)
        ws.write(row_c, 18, 'BI Op. Gvds dest. a op. No Grvds.', style_column)
        ws.write(row_c, 19, 'IGV', style_column)
        ws.write(row_c, 20, 'Valor Adq. No Gvds.', style_column)
        ws.write(row_c, 21, 'ISC', style_column)
        ws.write(row_c, 22, 'Otros', style_column)
        ws.write(row_c, 23, 'Importe Total', style_column)
        ws.write(row_c, 24, 'Moneda', style_column)
        ws.write(row_c, 25, 'T.C.', style_column)
        ws.write(row_c, 26, 'F.E. CP Modificado', style_column)
        ws.write(row_c, 27, 'T. CP. Modificado', style_column)
        ws.write(row_c, 28, 'Serie CP. Modificado', style_column)
        ws.write(row_c, 29, 'DUA', style_column)
        ws.write(row_c, 30, 'Correlativo CP. Modificado', style_column)
        ws.write(row_c, 31, 'F. Deposito Detracción', style_column)
        ws.write(row_c, 32, 'N° Constancia Detracción', style_column)
        ws.write(row_c, 33, 'Retención?', style_column)
        ws.write(row_c, 34, 'Clasificación de Bienes (Tabla 30)', style_column)
        ws.write(row_c, 35, 'Contrato o Proyecto?', style_column)
        ws.write(row_c, 36, 'E.T. 1', style_column)
        ws.write(row_c, 37, 'E.T. 2', style_column)
        ws.write(row_c, 38, 'E.T. 3', style_column)
        ws.write(row_c, 39, 'E.T. 4', style_column)
        ws.write(row_c, 40, 'M. Pago?', style_column)
        ws.write(row_c, 41, 'Estado', style_column)
        ws.write(row_c, 42, 'Libre', style_column)

        ws.set_row(row_c, 33)

        i = 0
        total_base_gdg = 0
        total_tax_gdg = 0
        total_base_gdm = 0
        total_tax_gdm = 0
        total_base_gdng = 0
        total_tax_gdng = 0
        total_amount_untaxed = 0
        total_isc = 0
        total_another_taxes = 0
        total_amount_total = 0

        for value in self.data_8_1:
            # if value['voucher_sunat_code'] not in ['91', '97', '98']:
            # ws.write(row_i + i, 0, i + 1, style_content)
            # ws.write(row_i + i, 1, value['period'], style_content)
            # ws.write(row_i + i, 2, value['number_origin'] or '', style_content)
            # ws.write(row_i + i, 3, value['journal_correlative'] or '', style_content)
            # ws.write(row_i + i, 4, value['date_invoice'] or '', style_date)
            # ws.write(row_i + i, 5, value['date_due'] or '', style_date)
            # ws.write(row_i + i, 6, value['voucher_sunat_code'] or '', style_content)
            # ws.write(row_i + i, 7, value['voucher_series'] or '', style_content)
            # ws.write(row_i + i, 8, value['voucher_year_dua_dsi'] or '', style_content)
            # ws.write(row_i + i, 9, value['correlative'] or '', style_content)
            # ws.write(row_i + i, 10, '', style_content)
            # ws.write(row_i + i, 11, value['customer_document_type'] or '', style_content)
            # ws.write(row_i + i, 12, value['customer_document_number'] or '', style_content)
            # ws.write(row_i + i, 13, value['customer_name'] or '', style_content)
            # ws.write(row_i + i, 14, value['base_gdg'], style_number)
            # ws.write(row_i + i, 15, value['tax_gdg'], style_number)
            # ws.write(row_i + i, 16, value['base_gdm'], style_number)
            # ws.write(row_i + i, 17, value['tax_gdm'], style_number)
            # ws.write(row_i + i, 18, value['base_gdng'], style_number)
            # ws.write(row_i + i, 19, value['tax_gdng'], style_number)
            # ws.write(row_i + i, 20, value['amount_untaxed'], style_number)
            # ws.write(row_i + i, 21, value['isc'], style_number)
            # ws.write(row_i + i, 22, value['another_taxes'], style_number)
            # ws.write(row_i + i, 23, value['amount_total'], style_number)
            # ws.write(row_i + i, 24, value['code_currency'] or '', style_content)
            # ws.write(row_i + i, 25, value['currency_rate'], style_number)
            # ws.write(row_i + i, 26, value['origin_date_invoice'] or '', style_date)
            # ws.write(row_i + i, 27, value['origin_document_code'] or '', style_content)
            # ws.write(row_i + i, 28, value['origin_serie'] or '', style_content)
            # ws.write(row_i + i, 29, value['origin_code_aduana'] or '', style_content)
            # ws.write(row_i + i, 30, value['origin_correlative'] or '', style_content)
            # ws.write(row_i + i, 31, value['voucher_date'] or '', style_date)
            # ws.write(row_i + i, 32, value['voucher_number'] or '', style_content)
            # ws.write(row_i + i, 33, value['retention'], style_number)
            # ws.write(row_i + i, 34, value['class_good_services'] or '', style_content)
            # ws.write(row_i + i, 35, value['irregular_societies'] or '', style_content)
            # ws.write(row_i + i, 36, value['error_exchange_rate'] or '', style_content)
            # ws.write(row_i + i, 37, value['supplier_not_found'] or '', style_content)
            # ws.write(row_i + i, 38, value['suppliers_resigned'] or '', style_content)
            # ws.write(row_i + i, 39, value['dni_ruc'] or '', style_content)
            # ws.write(row_i + i, 40, value['type_pay_invoice'] or '', style_content)
            # ws.write(row_i + i, 41, value['ple_state'] or '', style_content)
            ws.write(row_i + i, 0, i + 1, style_content)
            ws.write(row_i + i, 1, value['field_1'], style_content)
            ws.write(row_i + i, 2, value['field_2'] or '', style_content)
            ws.write(row_i + i, 3, value['field_3'] or '', style_content)
            ws.write(row_i + i, 4, value['field_4'] or '', style_date)
            ws.write(row_i + i, 5, value['field_5'] or '', style_date)
            ws.write(row_i + i, 6, value['field_6'] or '', style_content)
            ws.write(row_i + i, 7, value['field_7'] or '', style_content)
            ws.write(row_i + i, 8, value['field_8'] or '', style_content)
            ws.write(row_i + i, 9, value['field_9'] or '', style_content)
            ws.write(row_i + i, 10, value['field_10'], style_content)
            ws.write(row_i + i, 11, value['field_11'] or '', style_content)
            ws.write(row_i + i, 12, value['field_12'] or '', style_content)
            ws.write(row_i + i, 13, value['field_13'] or '', style_content)
            ws.write(row_i + i, 14, value['field_14'], style_number)
            ws.write(row_i + i, 15, value['field_15'], style_number)
            ws.write(row_i + i, 16, value['field_16'], style_number)
            ws.write(row_i + i, 17, value['field_17'], style_number)
            ws.write(row_i + i, 18, value['field_18'], style_number)
            ws.write(row_i + i, 19, value['field_19'], style_number)
            ws.write(row_i + i, 20, value['field_20'], style_number)
            ws.write(row_i + i, 21, value['field_21'], style_number)
            ws.write(row_i + i, 22, value['field_22'], style_number)
            ws.write(row_i + i, 23, value['field_23'], style_number)
            ws.write(row_i + i, 24, value['field_24'], style_number)
            ws.write(row_i + i, 25, value['field_25'], style_content)
            ws.write(row_i + i, 26, value['field_26'] or '', style_content)
            ws.write(row_i + i, 27, value['field_27'] or '', style_date)
            ws.write(row_i + i, 28, value['field_28'] or '', style_content)
            ws.write(row_i + i, 29, value['field_29'] or '', style_content)
            ws.write(row_i + i, 30, value['field_30'] or '', style_content)
            ws.write(row_i + i, 31, value['field_31'] or '', style_content)
            ws.write(row_i + i, 32, value['field_32'] or '', style_date)
            ws.write(row_i + i, 33, value['field_33'], style_number)
            ws.write(row_i + i, 34, value['field_34'], style_content)
            ws.write(row_i + i, 35, value['field_35'], style_content)

            ws.write(row_i + i, 36, value['field_36'], style_content)
            ws.write(row_i + i, 37, value['field_37'], style_content)
            ws.write(row_i + i, 38, value['field_38'], style_content)
            ws.write(row_i + i, 39, value['field_39'], style_content)
            ws.write(row_i + i, 40, value['field_40'], style_content)
            ws.write(row_i + i, 41, value['field_41'], style_content)
            ws.write(row_i + i, 42, value['field_42'], style_content)
            ws.write(row_i + i, 43, value['field_43'], style_content)

            # total_base_gdg += value['base_gdg']
            # total_tax_gdg += value['tax_gdg']
            # total_base_gdm += value['base_gdm']
            # total_tax_gdm += value['tax_gdm']
            # total_base_gdng += value['base_gdng']
            # total_tax_gdng += value['tax_gdng']
            # total_amount_untaxed += value['amount_untaxed']
            # total_isc += value['isc']
            # total_another_taxes += value['another_taxes']
            # total_amount_total += value['amount_total']
            i += 1

        # ws.write(total, 14, total_base_gdg, style_number_bold)
        # ws.write(total, 15, total_tax_gdg, style_number_bold)
        # ws.write(total, 16, total_base_gdm, style_number_bold)
        # ws.write(total, 17, total_tax_gdm, style_number_bold)
        # ws.write(total, 18, total_base_gdng, style_number_bold)
        # ws.write(total, 19, total_tax_gdng, style_number_bold)
        # ws.write(total, 20, total_amount_untaxed, style_number_bold)
        # ws.write(total, 21, total_isc, style_number_bold)
        # ws.write(total, 22, total_another_taxes, style_number_bold)
        # ws.write(total, 23, total_amount_total, style_number_bold)
        return True

    def _get_content_8_2(self, ws, style_header, style_column, style_number, style_number_bold, style_content, style_date):
        ws.set_column(0, 0, 4)
        ws.set_column(1, 1, 10)
        ws.set_column(2, 2, 14)
        ws.set_column(3, 3, 12)
        ws.set_column(4, 4, 10)
        ws.set_column(5, 5, 4)
        ws.set_column(6, 6, 6)
        ws.set_column(7, 7, 12)
        ws.set_column(8, 8, 17)
        ws.set_column(9, 9, 14)
        ws.set_column(10, 10, 17)
        ws.set_column(11, 11, 4)
        ws.set_column(12, 12, 6)
        ws.set_column(13, 13, 8)
        ws.set_column(14, 14, 12)
        ws.set_column(15, 15, 14)
        ws.set_column(16, 16, 5)
        ws.set_column(17, 17, 6)
        ws.set_column(18, 18, 10)
        ws.set_column(19, 19, 20)
        ws.set_column(20, 20, 20)
        ws.set_column(21, 21, 12)
        ws.set_column(22, 22, 20)
        ws.set_column(23, 23, 12)
        ws.set_column(24, 24, 4)
        ws.set_column(25, 25, 14)
        ws.set_column(26, 26, 14)
        ws.set_column(27, 27, 14)
        ws.set_column(28, 28, 6)
        ws.set_column(29, 29, 14)
        ws.set_column(30, 30, 4)
        ws.set_column(31, 30, 4)
        ws.set_column(32, 30, 4)
        ws.set_column(33, 30, 4)
        ws.set_column(34, 30, 3)
        ws.set_column(35, 30, 3)
        ws.set_column(36, 30, 3)

        header = 0
        total = header + 3
        row_c = total + 1
        row_i = row_c + 1

        ws.write(header, 0, 'Registro de Compras "No domiciliados" Formato 8.2, de la empresa {}'.format(
            self.obj.company_id.name
        ), style_header)
        ws.write(header + 1, 0, 'Por el periodo comprendio desde el {} al {}'.format(
            self.obj.date_start.strftime('%d/%m/%Y'),
            self.obj.date_end.strftime('%d/%m/%Y')
        ), style_header)
        ws.write(row_c, 0, 'Fila', style_column)
        ws.write(row_c, 1, 'Periodo', style_column)
        ws.write(row_c, 2, 'CUO', style_column)
        ws.write(row_c, 3, 'Correlativo', style_column)
        ws.write(row_c, 4, 'F. Emisión', style_column)
        ws.write(row_c, 5, 'Tipo Doc.', style_column)
        ws.write(row_c, 6, 'Serie', style_column)
        ws.write(row_c, 7, 'Correlativo', style_column)
        ws.write(row_c, 8, 'Valor Adquisiciones', style_column)
        ws.write(row_c, 9, 'Otros Conceptos', style_column)
        ws.write(row_c, 10, 'Importe Total', style_column)
        ws.write(row_c, 11, 'Tipo Doc. Origen', style_column)
        ws.write(row_c, 12, 'Serie C.P. Sustento', style_column)
        ws.write(row_c, 13, 'Año DUA', style_column)
        ws.write(row_c, 14, 'Correlativo CP. Sustento.', style_column)
        ws.write(row_c, 15, 'Ret.IGV', style_column)
        ws.write(row_c, 16, 'Moneda', style_column)
        ws.write(row_c, 17, 'T.C.', style_column)
        ws.write(row_c, 18, 'País Residencia', style_column)
        ws.write(row_c, 19, 'Nombre o Razon Social', style_column)
        ws.write(row_c, 20, 'Domicilio en extranjero', style_column)
        ws.write(row_c, 21, 'Identificación fiscal beneficiario', style_column)
        ws.write(row_c, 22, 'Nombre o Razon Social beneficiario efectivo de los pagos', style_column)
        ws.write(row_c, 23, 'País residencia del Beneficiario', style_column)
        ws.write(row_c, 24, 'Vínculo', style_column)
        ws.write(row_c, 25, 'Renta Bruta', style_column)
        ws.write(row_c, 26, 'Deducción / Costo venta bienes capital', style_column)
        ws.write(row_c, 27, 'Renta Neta', style_column)
        ws.write(row_c, 28, 'Tasa de retención', style_column)
        ws.write(row_c, 29, 'Impuesto retenido', style_column)
        ws.write(row_c, 30, 'CDI', style_column)
        ws.write(row_c, 31, 'Ex. aplicada', style_column)
        ws.write(row_c, 32, 'Tipo de Renta', style_column)
        ws.write(row_c, 33, 'Modalida', style_column)
        ws.write(row_c, 34, 'Art. 76°?', style_column)
        ws.write(row_c, 35, 'Estado', style_column)
        ws.write(row_c, 36, 'Libre', style_column)

        ws.set_row(row_c, 33)

        i = 0
        total_amount_untaxed = 0
        total_another_taxes = 0
        total_amount_total = 0
        total_inv_retention_igv = 0

        for value in self.data_8_2:
            # if value['voucher_sunat_code'] in ['00', '91', '97', '98'] and value['partner_nodomicilied']:
            # ws.write(row_i + i, 0, i + 1, style_content)
            # ws.write(row_i + i, 1, value['period'] or '', style_content)
            # ws.write(row_i + i, 2, value['number_origin'] or '', style_content)
            # ws.write(row_i + i, 3, value['journal_correlative'] or '', style_content)
            # ws.write(row_i + i, 4, value['date_invoice'] or '', style_date)
            # ws.write(row_i + i, 5, value['voucher_sunat_code'] or '', style_content)
            # ws.write(row_i + i, 6, value['voucher_series'] or '', style_content)
            # ws.write(row_i + i, 7, value['correlative'] or '', style_content)
            # ws.write(row_i + i, 8, value['amount_untaxed'], style_number)
            # ws.write(row_i + i, 9, value['another_taxes'], style_number)
            # ws.write(row_i + i, 10, value['amount_total'], style_number)
            # ws.write(row_i + i, 11, value['inv_type_document'] or '', style_content)
            # ws.write(row_i + i, 12, value['inv_serie'] or '', style_content)
            # ws.write(row_i + i, 13, value['inv_year_dua_dsi'] or '', style_content)
            # ws.write(row_i + i, 14, value['inv_correlative'] or '', style_content)
            # ws.write(row_i + i, 15, value['inv_retention_igv'], style_number)
            # ws.write(row_i + i, 16, value['code_currency'] or '', style_content)
            # ws.write(row_i + i, 17, value['currency_rate'], style_number)
            # ws.write(row_i + i, 18, value['country_code'] or '', style_content)
            # ws.write(row_i + i, 19, value['customer_name'] or '', style_content)
            # ws.write(row_i + i, 20, value['partner_street'] or '', style_content)
            # ws.write(row_i + i, 21, '', style_content)
            # ws.write(row_i + i, 22, '', style_content)
            # ws.write(row_i + i, 23, '', style_content)
            # ws.write(row_i + i, 24, value['linkage_code'] or '', style_content)
            # ws.write(row_i + i, 25, value['hard_rent'], style_number)
            # ws.write(row_i + i, 26, value['deduccion_cost'], style_number)
            # ws.write(row_i + i, 27, value['rent_neta'], style_number)
            # ws.write(row_i + i, 28, value['retention_rate'], style_number)
            # ws.write(row_i + i, 29, value['tax_withheld'], style_number)
            # ws.write(row_i + i, 30, value['cdi'] or '', style_content)
            # ws.write(row_i + i, 31, value['exoneration_nodomicilied_code'] or '', style_content)
            # ws.write(row_i + i, 32, value['type_rent'] or '', style_content)
            # ws.write(row_i + i, 33, value['taken_code'] or '', style_content)
            # ws.write(row_i + i, 34, value['application_article'] or '', style_content)
            # ws.write(row_i + i, 35, value['ple_state'] or '', style_content)
            ws.write(row_i + i, 0, i + 1, style_content)
            ws.write(row_i + i, 1, value['field_1'], style_content)
            ws.write(row_i + i, 2, value['field_2'] or '', style_content)
            ws.write(row_i + i, 3, value['field_3'] or '', style_content)
            ws.write(row_i + i, 4, value['field_4'] or '', style_date)
            ws.write(row_i + i, 5, value['field_5'] or '', style_date)
            ws.write(row_i + i, 6, value['field_6'] or '', style_content)
            ws.write(row_i + i, 7, value['field_7'] or '', style_content)
            ws.write(row_i + i, 8, value['field_8'] or '', style_content)
            ws.write(row_i + i, 9, value['field_9'] or '', style_content)
            ws.write(row_i + i, 10, value['field_10'], style_content)
            ws.write(row_i + i, 11, value['field_11'] or '', style_content)
            ws.write(row_i + i, 12, value['field_12'] or '', style_content)
            ws.write(row_i + i, 13, value['field_13'] or '', style_content)
            ws.write(row_i + i, 14, value['field_14'], style_number)
            ws.write(row_i + i, 15, value['field_15'], style_number)
            ws.write(row_i + i, 16, value['field_16'], style_number)
            ws.write(row_i + i, 17, value['field_17'], style_number)
            ws.write(row_i + i, 18, value['field_18'], style_number)
            ws.write(row_i + i, 19, value['field_19'], style_number)
            ws.write(row_i + i, 20, value['field_20'], style_number)
            ws.write(row_i + i, 21, value['field_21'], style_number)
            ws.write(row_i + i, 22, value['field_22'], style_number)
            ws.write(row_i + i, 23, value['field_23'], style_number)
            ws.write(row_i + i, 24, value['field_24'], style_number)
            ws.write(row_i + i, 25, value['field_25'], style_content)
            ws.write(row_i + i, 26, value['field_26'] or '', style_content)
            ws.write(row_i + i, 27, value['field_27'] or '', style_date)
            ws.write(row_i + i, 28, value['field_28'] or '', style_content)
            ws.write(row_i + i, 29, value['field_29'] or '', style_content)
            ws.write(row_i + i, 30, value['field_30'] or '', style_content)
            ws.write(row_i + i, 31, value['field_31'] or '', style_content)
            ws.write(row_i + i, 32, value['field_32'] or '', style_date)
            ws.write(row_i + i, 33, value['field_33'], style_number)

            # total_amount_untaxed += value['amount_untaxed']
            # total_another_taxes += value['another_taxes']
            # total_amount_total += value['amount_total']
            # total_inv_retention_igv += value['inv_retention_igv']
            i += 1

        # ws.write(total, 8, total_amount_untaxed, style_number_bold)
        # ws.write(total, 9, total_another_taxes, style_number_bold)
        # ws.write(total, 10, total_amount_total, style_number_bold)
        # ws.write(total, 15, total_inv_retention_igv, style_number_bold)
        return True

    def get_content(self, type_report='1'):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        style_header = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
        })
        style_column = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style_content = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'border': 7
        })
        style_number = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'border': 7
        })
        style_number_bold = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'bold': True,
            'border': 7
        })
        style_date = workbook.add_format({
            'size': 10,
            'num_format': 'dd/mm/yy',
            'border': 7
        })
        ws = workbook.add_worksheet('Report de Compras')
        if type_report == '1':
            self._get_content_8_1(
                ws,
                style_header,
                style_column,
                style_number,
                style_number_bold,
                style_content,
                style_date
            )
        else:
            self._get_content_8_2(
                ws,
                style_header,
                style_column,
                style_number,
                style_number_bold,
                style_content,
                style_date
            )

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self, month, year, company, type='01'):
        if type == '01':
            return f'RC_{year}_{month}_{company}_8.1.xlsx'
        else:
            return f'RC_{year}_{month}_{company}_8.2.xlsx'
