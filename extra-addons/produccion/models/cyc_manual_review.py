from odoo import models, fields

class CycManualReview(models.Model):
    _name = 'cyc.manual.review'
    _description = 'Manual Review for Incidents'

    name = fields.Selection([
        ('cyc.afp', 'AFP'),
        ('cyc.prorroga', 'Prórroga'),
        ('cyc.siniestro', 'Siniestro'),
        ('cyc.clasificacion', 'Clasificación'),
    ], string="Modelo Relacionado")