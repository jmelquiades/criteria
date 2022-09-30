from odoo import _, api, fields, models


class PleBaseLine(models.Model):
    _name = 'ple.base.line'
    _description = 'ple.base.line'

    ple_base_id = fields.Many2one('ple.base', string='Ple Base')
    move_id = fields.Many2one('account.move', string='move')
