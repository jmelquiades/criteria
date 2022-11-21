from odoo import _, api, fields, models
import base64

from bs4 import BeautifulSoup
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    import_xml = fields.Binary('Líneas de pedido XML')

    def import_xml_from_sale_order_line(self):
        xml = self.import_xml
        content = base64.b64decode(xml)
        # data

        # Passing the stored data inside
        # the beautifulsoup parser, storing
        # the returned object
        Bs_data = BeautifulSoup(content, "xml")

        # Finding all instances of tag
        # `unique`
        order_line = Bs_data.find_all('row')
        records = []
        for ol in order_line:
            fields = ol.find_all('column')
            fields = map(lambda c: c.text.strip(), fields)
            fields = list(fields)
            family, default_code, product_name, unit_name, quantity = fields
            product = self.env['product.product'].search([('default_code', '=', default_code)])
            product = product[0] if product else False
            product_uom = self.env['uom.uom'].search([('name', '=', unit_name)])
            product_uom = product_uom[0] if product_uom else False
            quantity = float(quantity)
            if all([product, product_uom, quantity]):
                data = {
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                    'product_uom': product_uom.id,
                }
                self.order_line = [(0, 0, data)]
            else:
                if not product:
                    raise UserError(f'El producto {product_name} con código {default_code} no existe, considere crearlo para poder importar el pedido.')
                if not product_uom:
                    raise UserError(f'La unidad de medida {unit_name} no existe, considere crearlo para poder importar el pedido.')
