from odoo import models, fields

class CycExtension(models.Model):
    _name = 'cyc.extension'
    _description = 'CyC Extension'
    #_order = 'date_due desc'
    _inherit = 'cyc.api.mixin'

    # RELATIONS

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')
    cyc_collection_id = fields.Many2one('cyc.collection', string='Cobro')
    cyc_manual_review_id = fields.Many2one('cyc.manual.review', string='Revisión Manual')
    currency_id = fields.Many2one('res.currency', string='Moneda')

    # FIELDS

    status1 = fields.Selection(selection=[
        ('open', 'Abierta'),
        ('historic', 'Histórica'),
    ], string='Estado', default='open')