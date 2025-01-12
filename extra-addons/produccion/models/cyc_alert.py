from odoo import models, fields

class CycAlert(models.Model):
    _name = 'cyc.alert'
    _description = 'CyC Alert'
    #_order = 'date desc'

    # RELATIONS

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')

    # FIELDS

    status = fields.Selection(selection=[  
        ('new', 'Nueva'),
        ('historic', 'Histórico'),
    ], string='Estado', default='new')