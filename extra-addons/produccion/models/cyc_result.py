from odoo import models, fields

class CycResult(models.Model):
    _name = 'cyc.result'
    _description = 'CyC Result'

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')

    # FIELDS

    status = fields.Selection(selection=[  
        ('last', 'Último'),
        ('historic', 'Histórico'),
    ], string='Estado', default='last')