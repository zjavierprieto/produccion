from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import requests

class RiesgoAfp(models.Model):
    _name = 'riesgo.afp'
    _description = 'AFP de Riesgo'

    # RIESGO

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)

    # FACTURAS FALTA REQUIRED EN PRO Y SIN TAMBIEN

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos', ondelete='cascade')
    numero_vencimientos = fields.Integer(string="Número de Vencimientos", compute='_compute_numero_vencimientos')

    fecha_comunicacion = fields.Date(string='Fecha de Comunicación')
    fecha_comunicacion_cancelacion = fields.Date(string='Fecha de Comunicación de Cancelación')
    importe_impagado = fields.Float(string='Importe Impagado')
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento')
    observacion = fields.Char(string='Observación')
    mensaje = fields.Char(string='Mensaje')
    error = fields.Char(string='Error')
    cyc_alerta = fields.Char(string='CyC Alerta')
    motivo_estado = fields.Char(string='Motivo del Estado')    
    estado = fields.Selection([
        ('Comunicado', 'Comunicado'), 
        ('Pendiente', 'Pendiente'),
        ('Cancelado', 'Cancelado'), 
        ('Rechazado', 'Rechazado')
        ], string='Estado', default='Pendiente')
    status = fields.Selection([
        # Pendiente:
        ('Pendiente de Validar', 'Pendiente de Validar'), # Enviada a CyC
        ('Validada', 'Validada'), # Validada por CyC
        ('Error de Validacion', 'Error de Validación'),
        ('Pendiente de Respuesta', 'Pendiente de Respuesta'), # Respuesta de CyC "PENDIENTE"
        ('Pendiente de Comunicar', 'Pendiente de Comunicar'), # Respuesta de CyC correcta
        ('Pendiente de Cancelar', 'Pendiente de Cancelar'), # Respuesta de CyC correcta
        ('Error de Respuesta', 'Error de Respuesta')
        ], string='Status', default='Pendiente de Validar')
    moneda = fields.Selection([
        ('EUR', 'EUR'), 
        ('USD','USD'), 
        ('GBP', 'GBP'), 
        ('BRL', 'BRL')
        ], string="Moneda", default='EUR') 

    # Campo para mostrar el nombre del cliente en la vista de AFP
    display_name = fields.Char(compute='_compute_display_info', string="Cliente", store=True)

    @api.depends('riesgo_id', 'riesgo_id.name')
    def _compute_display_info(self):
        for record in self:
            record.display_name = record.riesgo_id.name

    # -------------
    # Eliminar AFP
    # -------------

    def action_cancel_afp(self):
        self.cancel_afp_to_api()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def cancel_afp_to_api(self):
        client_id = 'CRISCOLOR' 
        url = f'http://web:5003/api/v1/{client_id}/cancel_afp'
        headers = {'Content-Type': 'application/json'}
        
        fecha_vencimiento_str = self.fecha_vencimiento.strftime('%Y-%m-%d')

        payload = {
            "importe_impagado":  self.importe_impagado,
            "moneda": self.moneda,
            "fecha_vencimiento": fecha_vencimiento_str,
            "vat": self.riesgo_id.vat,
            "razon_social": self.riesgo_id.name,
            "country": self.riesgo_id.country_id.name if self.riesgo_id.country_id else '',
        }

        try:
            response = requests.put(url, json=payload, headers=headers)
            if response.status_code == 200:
                self.estado = 'Pendiente'
                self.status = 'Pendiente de Cancelar'
            else:
                raise UserError(f"Error '{response.status_code}'. Comnuíquese con Tecletes.")
        except requests.exceptions.RequestException as e:
            raise UserError(f"Error: '{str(e)}'. Comnuíquese con Tecletes.")
        return

    # ----------------
    # Ver Vencimientos
    # ----------------

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
