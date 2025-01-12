from odoo import models, fields

class CycCollection(models.Model):
    _name = 'cyc.collection'
    _description = 'CyC Collection'
    #_order = 'date_due desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cyc.api.mixin']

    move_id = fields.Many2one('account.move', string='Factura Relacionada', ondelete='restrict')
    move_line_id = fields.Many2one('account.move.line', string='Cobro Relacionado', unique=True, ondelete='restrict')
    currency_id = fields.Many2one('res.currency', string='Moneda')

    cyc_afp_ids = fields.One2many('cyc.afp', 'cyc_collection_id', string='AFPs', ondelete="restrict")
    cyc_extension_ids = fields.One2many('cyc.extension', 'cyc_collection_id', string='Prórrogas', ondelete="restrict")
    cyc_claim_id = fields.Many2one('cyc.claim', string='Siniestro', ondelete="restrict")

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')
    cyc_contact_id = fields.Many2one('cyc.contact', string='Sucursal', ondelete='restrict')