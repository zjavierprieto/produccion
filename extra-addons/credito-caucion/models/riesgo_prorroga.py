from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import requests

class RiesgoProrroga(models.Model):
    _name = 'riesgo.prorroga'
    _description = 'Prórroga de Riesgo'


    # RIESGO

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)

    # FACTURAS

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos', ondelete='cascade')
    numero_vencimientos = fields.Integer(string="Número de Vencimientos", compute='_compute_numero_vencimientos')
    
    # FIELDS

    importe_prorrogado = fields.Float(string='Importe Prorrogado')
    fecha_comunicacion = fields.Date(string='Fecha de Comunicación')
    fecha_comunicacion_cancelacion = fields.Date(string='Fecha de Comunicación de Cancelación')
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento Primitivo')
    fecha_vencimiento_prorroga = fields.Date(string='Fecha de Nuevo Vencimiento')

    documento_pago = fields.Binary('Documento Pago')
    documento_pago_nombre = fields.Char('Documento Pago')
    observacion = fields.Char(string='Observación')
    mensaje = fields.Char(string='Mensaje')
    error = fields.Char(string='Error')
    motivo_estado = fields.Char(string='Motivo del Estado')
    estado = fields.Selection([
        ('Comunicada', 'Comunicada'), 
        ('Pendiente', 'Pendiente'),
        ('Cancelada', 'Cancelada'), 
        ('Rechazada', 'Rechazada')
        ], string='Estado', default='Pendiente')
    status = fields.Selection([
        ('RESOLUCION', 'RESOLUCION'), 
        ('PENDIENTE', 'PENDIENTE'), 
        ('ERROR', 'ERROR'),
        ('Pendiente de Comunicar', 'Pendiente de Comunicar'),
        ('Pendiente de Cancelar', 'Pendiente de Cancelar')
        ], string='Status', default='PENDIENTE')
    moneda = fields.Selection([
        ('EUR', 'EUR'), 
        ('USD','USD'), 
        ('GBP', 'GBP'), 
        ('BRL', 'BRL')
        ], string="Moneda", default='EUR') 

    # DISPLAY NAME

    display_name = fields.Char(compute='_compute_display_info', string="Cliente", store=True)

    @api.depends('riesgo_id', 'riesgo_id.name')
    def _compute_display_info(self):
        for record in self:
            record.display_name = record.riesgo_id.name

    # ------------------------
    # Enviar Documento de Pago
    # ------------------------

    def send_mail_documento_pago(self):
        email_to = 'zjavierprieto@gmail.com'  
        subject = 'Comunicación Prorroga'
        body = f'Te adjunto el documento de pago en referencia a la Prórroga que acabo de declarar sobre el cliente {self.riesgo_id.name} con NIF: {self.riesgo_id.vat}.'
        self.doc_pago_name = f'{self.riesgo_id.vat}'
        try:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'attachment_ids': [(0, 0, {
                    'name': self.doc_pago_name,
                    'datas': self.doc_pago,
                    'type': 'binary',
                    'res_model': 'mail.compose.message',
                })],
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
        except Exception as e:
            raise UserError(f"Failed to send email: {str(e)}")
    
    # -----------------
    # Eliminar Prórroga
    # -----------------

    def action_cancel_prorroga(self):
        self.cancel_prorroga_to_api()
        return { 'type': 'ir.actions.client', 'tag': 'reload',}

    def cancel_prorroga_to_api(self):
        client_id = 'CRISCOLOR'  
        url = f'http://web:5003/api/v1/{client_id}/cancel_prorroga' 
        headers = {'Content-Type': 'application/json'}

        fecha_vencimiento_str = self.fecha_vencimiento.strftime('%Y-%m-%d')
        fecha_vencimiento_pro_str = self.fecha_vencimiento_prorroga.strftime('%Y-%m-%d')

        payload = {
            "importe_prorrogado": self.importe_prorrogado,
            "moneda": self.moneda,
            "fecha_vencimiento": fecha_vencimiento_str,
            "fecha_vencimiento_pro": fecha_vencimiento_pro_str,
            
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
