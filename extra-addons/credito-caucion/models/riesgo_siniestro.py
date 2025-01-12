from odoo import models, fields, api

class RiesgoSiniestro(models.Model):
    _name = 'riesgo.siniestro'
    _description = 'Siniestro de Riesgo'

    # RIESGO

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)

    # FACTURAS

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos', ondelete='cascade')
    numero_vencimientos = fields.Integer(string="Número de Vencimientos", compute='_compute_numero_vencimientos')
    
    numero = fields.Integer(string='Número')
    fecha_declaracion = fields.Date(string='Fecha de Declaración')
    credito_total = fields.Float(string='Crédito Total')
    fecha_impago = fields.Date(string='Fecha Impago')
    fecha_comunicacion = fields.Date(string='Fecha Comunicación')
    credito_asegurado = fields.Float(string='Crédito Asegurado')
    porcentaje_garantia = fields.Integer(string='Porcentaje de Garantía')
    gestor = fields.Char(string='Gestor')
    situacion = fields.Char(string='Situación')
    estado = fields.Selection([
        ('Abierto', 'Abierto'), 
        ('Pendiente', 'Pendiente'),
        ('Anulado', 'Anulado'), 
        ('Terminado', 'Terminado'),
        ], string='Estado', default='Pendiente')
    fuera_de_seguro = fields.Selection([
        ('Si', 'Sí'), 
        ('No', 'No')
        ], string='Fuera de Seguro')
    documentos_ids = fields.Many2many(
        'ir.attachment',
        string="Documentos",
        help="Adjuntar todos los documentos relacionados con el impago. (Facturas, Albaranes, Pagarés, Certificados de Entrega, Recibos devueltos, Si es Exterior el BL...)"
    )

    # Campo para mostrar el nombre del cliente en la vista de siniestros
    display_name = fields.Char(compute='_compute_display_info', string="Cliente", store=True)

    @api.depends('riesgo_id', 'riesgo_id.name')
    def _compute_display_info(self):
        for record in self:
            record.display_name = record.riesgo_id.name

    # -----------
    # Ver Factura
    # -----------

    @api.depends('vencimiento_ids')
    def _compute_numero_vencimientos(self):
        for record in self:
            # Contar cuántos vencimientos están asociados a la incidencia
            record.numero_vencimientos = len(record.vencimiento_ids)


    def action_view_vencimiento(self):
        """Abrir los vencimientos relacionados con esta incidencia."""
        if self.vencimiento_ids:
            if len(self.vencimiento_ids) == 1:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.move.line',
                    'name': 'Cobro',
                    'view_mode': 'form',
                    'view_id': self.env.ref('credito-caucion.view_gestor_cobros_form').id,
                    'res_id': self.vencimiento_ids[0].id,
                    'target': 'current',
                }
            else:
                domain = [('id', 'in', self.vencimiento_ids.ids)]

                # Devuelve la acción con el dominio dinámico
                action = self.env.ref('credito-caucion.action_gestor_cobros').read()[0]
                action['domain'] = domain
                
                return action
        else:
            return {'type': 'ir.actions.act_window_close'}
