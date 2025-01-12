from odoo import models, fields

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='restrict')
