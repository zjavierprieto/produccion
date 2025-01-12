from odoo import models, fields

class CycAfp(models.Model):
    _name = 'cyc.afp'
    _description = 'CyC AFP'
    #_order = 'date_due desc'
    _inherit = 'cyc.api.mixin'


    # RELATIONS

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')
    cyc_collection_id = fields.Many2one('cyc.collection', string='Cobro')
    cyc_manual_review_id = fields.Many2one('cyc.manual.review', string='Revisión Manual')
    currency_id = fields.Many2one('res.currency', string='Moneda')

    # FIELDS

    amount_unpaid = fields.Monetary(string='Unpaid Amount', required=True)
    due_date = fields.Date(string='Due Date', required=True)

    communication_date = fields.Date(string='Communication Date', required=True)
    observation = fields.Char(string='Observation')
    cyc_alert = fields.Char(string='CyC Alert')

    cancellation_date = fields.Date(string='Cancellation Date')
    
    message = fields.Char(string='Message')  
    error = fields.Char(string='Error')

    # FIELDS (reporting)

    status1 = fields.Selection(selection=[
        ('open', 'Abierto'),
        ('historic', 'Histórico'),
    ], string='Estado', default='open')

    status = fields.Selection([
        ('communicated', 'Communicated'), 
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'), 
        ('rejected', 'Rejected')
    ], string='Status', default='pending', required=True)

    status2 = fields.Selection([
        ('validation error', 'Error en la Validación'),
        ('response error', 'Error en la Respuesta'),
        ('pending classification', 'Pendiente de Comunicar'), 
        ('pending cancelation', 'Pendiente de Cancelar'), 
        ('canceled', 'Cancelado'),
        ('refused', 'Rehusado'),
    ], string='Estado', default='pending classification')

    reason = fields.Char(string='Reason')  