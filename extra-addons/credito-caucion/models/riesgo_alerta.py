from odoo import models, fields, api

class RiesgoAlerta(models.Model):
    _name = 'riesgo.alerta'
    _description = 'Alerta de Riesgo'

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)
    
    fecha = fields.Date(string='Fecha')
    descripcion = fields.Char(string='Descripción')
    estado = fields.Selection([
        ('Nueva', 'Nueva'),
        ('Vista', 'Vista'),
    ], string = 'Estado')

    # Campo para mostrar el nombre del cliente en la vista de siniestros
    display_name = fields.Char(compute='_compute_display_info', string="Cliente", store=True)

    @api.depends('riesgo_id', 'riesgo_id.name')
    def _compute_display_info(self):
        for record in self:
            record.display_name = record.riesgo_id.name

    # ------------------------
    # Marcar Alerta como Vista
    # ------------------------

    def action_mark_as_read(self):
        self.estado = 'Vista'
        return {'type': 'ir.actions.act_window_close'}