from odoo import models, fields

class CycClaim(models.Model):
    _name = 'cyc.claim'
    _description = 'CyC Claim'
    #_order = 'date desc'
    _inherit = 'cyc.api.mixin'

    # RELATIONS

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')
    cyc_collection_ids = fields.One2many('cyc.collection', 'cyc_claim_id', string='Cobros')
    cyc_manual_review_id = fields.Many2one('cyc.manual.review', string='Revisión Manual')
    currency_id = fields.Many2one('res.currency', string='Moneda',)

    # FIELDS

    status1 = fields.Selection(selection=[
        ('open', 'Abierto'),
        ('historic', 'Histórico'),
    ], string='Estado', default='open')
