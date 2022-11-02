from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_correlative = fields.Selection(
        selection=[
            ('A', 'Apertura'),
            ('C', 'Cierre'),
            ('M', 'Movimiento')
        ],
        default='M',
        string='Estado PLE'
    )
    no_include_ple = fields.Boolean(
        string='No includir en Registro del PLE',
        default=False,
        help="""
Si este campo está marcado, las facturas (documentos de compra y venta), que tengan este diario seteado, no aparecerán en el registro de compras o ventas del PLE. Sin perjuicio de que los asientos contables que dichas facturas generen, aparecerán en los libros que se elaboren con base a los asientos contables, como son el Libro Diario y Mayor.
"""
    )
