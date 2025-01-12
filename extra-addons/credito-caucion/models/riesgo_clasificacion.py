from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import requests

class RiesgoClasificacion(models.Model):
    _name = 'riesgo.clasificacion'
    _description = 'Clasificación de Riesgo'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    # Required Fields (Before Request)

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)
    importe_solicitado = fields.Float(string='Importe Solicitado', required=True)
    fecha_solicitud = fields.Date(string='Fecha de Solicitud', required=True)

    # Answer Fields (After Request)

    importe_concedido = fields.Float(string='Importe Concedido')
    fecha_comunicacion_eliminacion = fields.Date(string='Fecha de Comunicación de Eliminación')
    fecha_clasificacion = fields.Date(string='Fecha de Clasificación')
    fecha_desclasificacion = fields.Date(string='Fecha de Desclasificación') # En caso de mandarla al historial
    motivo = fields.Char(string='Motivo')
    mensaje = fields.Char(string='Mensaje')
    error = fields.Char(string='Error')
    estado = fields.Selection([
        ('En Vigor', 'En vigor'), 
        ('Pendiente', 'Pendiente'),
        ('Historico', 'Histórico'), 
    ], string='Estado', default='En Estudio')
    status = fields.Selection([
        # En vigor:
        ('RESOLUCION', 'RESOLUCION'), 
        ('PROVISIONAL', 'PROVISIONAL'), 
        ('REDUCCION', 'REDUCCION'), 
        ('REHABILITACION', 'REHABILITACION'), 

        # Pendiente:
        ('Pendiente de Validar', 'Pendiente de Validar'), # Enviada a CyC
        ('Validada', 'Validada'), # Validada por CyC
        ('Error de Validacion', 'Error de Validación'),
        ('En estudio', 'En estudio'), # Respuesta de CyC "PENDIENTE"
        ('Pendiente de Clasificar', 'Pendiente de Clasificar'), # Respuesta de CyC correcta
        ('Pendiente de Desclasificar', 'Pendiente de Desclasificar'), # Respuesta de CyC correcta
        ('Error de Respuesta', 'Error de Respuesta'), 
        
        # Histórico:
        ('Reshusada por CyC', 'Rehusada por CyC'),
        ('Rehusada por Nosotros', 'Rehusada por Nosotros')

    ], string='Status', default='PENDIENTE')
    duracion = fields.Selection([
        ('30', '30 días'), 
        ('60', '60 días'), 
        ('90', '90 días'),
        ('Indefinida', 'Indefinida')
        ], string="Duración", default='Indefinida')

    # Optional Fields

    importe_concedido_empresa = fields.Float(string='Concedido Empresa')

    # Campo para mostrar el nombre del cliente en la vista de clasificaciones
    display_name = fields.Char(compute='_compute_display_info', string="Cliente", store=True)

    @api.depends('riesgo_id', 'riesgo_id.name')
    def _compute_display_info(self):
        for record in self:
            record.display_name = record.riesgo_id.name
    
    # ----------------------
    # Eliminar Clasificación
    # ----------------------

    def action_delete_clasificacion(self):
        self.delete_classification_to_api()
        return {'type': 'ir.actions.client', 'tag': 'reload',}
    
    def delete_classification_to_api(self):
        client_id = 'CRISCOLOR' 
        url = f'http://web:5003/api/v1/{client_id}/delete_classification'
        headers = {'Content-Type': 'application/json'}
        
        fecha_clasificacion_str = self.fecha_clasificacion.strftime('%Y-%m-%d')

        payload = {
            "importe_concedido":  self.importe_concedido,
            "fecha_clasificacion": fecha_clasificacion_str,   
            "vat": self.riesgo_id.vat,
            "contador": 0,
            "expediente": self.riesgo_id.expediente,
            "razon_social": self.riesgo_id.name,   
            "provincia": self.riesgo_id.state_id.name if self.riesgo_id.state_id else '',
            "pais": self.riesgo_id.country_id.name if self.riesgo_id.country_id else '',
        }

        try:
            response = requests.put(url, json=payload, headers=headers)
            if response.status_code == 200:
                self.estado = 'Pendiente'
                self.status = 'Pendiente de Desclasificar'
            else:
                raise UserError(f"Error '{response.status_code}'. Comnuíquese con Tecletes.")
        except requests.exceptions.RequestException as e:
            raise UserError(f"Error: '{str(e)}'. Comnuíquese con Tecletes.")
        return

    @api.model
    def action_reducir_clasificacion(self):
        return
        
    @api.model
    def action_eliminar_clasificacion(self):
        return

