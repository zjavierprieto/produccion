from odoo import models, fields

class CycClassification(models.Model):
    _name = 'cyc.classification'
    _description = 'CyC Classification'
    _inherit = 'cyc.api.mixin'

    # RELATIONS

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente', ondelete='restrict')
    cyc_manual_review_id = fields.Many2one('cyc.manual.review', string='Revisión Manual')

    currency_id = fields.Many2one('res.currency', string='Moneda')

    # FIELDS

    amount_requested = fields.Monetary(string='Importe Solicitado', currency_field='currency_id')
    amount_granted = fields.Monetary(string='Importe Concedido', currency_field='currency_id', default=0)

    date_request = fields.Date(string='Fecha de Solicitud')
    date_validation = fields.Date(string='Fecha de Validación')
    date_response = fields.Date(string='Fecha de Respuesta')
    date_classification = fields.Date(string='Fecha de Clasificación')
    date_eliminated = fields.Date(string='Fecha de Eliminación')

    note = fields.Char(string='Nota')
    reason = fields.Char(string='Motivo')
    
    message = fields.Char(string='Mensaje')
    error = fields.Char(string='Error')
   
    status1 = fields.Selection(selection=[
        ('in force', 'Vigor'),
        ('historic', 'Histórico'),
    ], string='Situación', default='in force')

    status2 = fields.Selection([
        ('validation error', 'Error en la Validación'),
        ('response error', 'Error en la Respuesta'),
        ('pending classification', 'Pendiente de Clasificar'), 
        ('pending amplification', 'Pendiente de Ampliar'), 
        ('pending reduction', 'Pendiente de Reducir'), 
        ('pending elimination', 'Pendiente de Eliminar'),
        ('correct', 'Correcto'),
        ('limited', 'Limitada por CyC'),
        ('refused cyc', 'Rehusada por CyC'),
        ('refused us', 'Rehusada por Nosotros')
    ], string='Estado', default='pending classification')