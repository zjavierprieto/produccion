from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import requests

class CreateRiesgoProrroga(models.TransientModel):
    _name = 'create.riesgo.prorroga'
    _description = 'Wizard para comunicar una prórroga'

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos Asociados', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento Primitivo', required=True)
    fecha_vencimiento_prorroga = fields.Date(string='Fecha de Nuevo Vencimiento', required=True)
    importe_prorrogado = fields.Float(string='Importe Prorrogado', required=True)
    documento_pago = fields.Binary(string='Documento de Pago', required=True)
    documento_pago_nombre = fields.Char(string='Documento Pago')
    observacion = fields.Char(string='Observación')

    def action_create_prorroga(self):
        riesgo_id = self.env.context.get('default_riesgo_id')
        vencimiento_ids = self.env.context.get('default_vencimiento_ids')
       
        if not riesgo_id:
            raise UserError("No se ha especificado el perfil de riesgo asociado.")
        
        riesgo = self.env['riesgo'].browse(riesgo_id)
        if not riesgo.exists():
            raise UserError("El registro de Riesgo no existe.")

        # Verificar si `vencimiento_ids` es un solo ID o una lista
        if isinstance(vencimiento_ids, int):
            vencimientos = self.env['account.move.line'].browse([vencimiento_ids])  # Si es un entero, lo convertimos en una lista
        elif isinstance(vencimiento_ids, list):
            vencimientos = self.env['account.move.line'].browse(vencimiento_ids)  # Si ya es una lista, la usamos directamente
        else:
            raise UserError("No se han especificado los vencimientos asociados correctamente.")
        
        if not vencimientos.exists():
            raise UserError("Los registros de vencimientos no existen.")

        if not self.documento_pago:
            raise ValidationError('Debe adjuntar un documento PDF.')
        if not self.importe_prorrogado:
            raise ValidationError("Por favor, complete el Importe Prorrogado.")
        if not self.fecha_vencimiento:
            raise ValidationError("Por favor, complete la Fecha de Vencimiento Primitiva.")
        if not self.fecha_vencimiento_prorroga:
            raise ValidationError("Por favor, complete la Fecha de Vencimiento de la Prórroga.")
        if self.fecha_vencimiento_prorroga <= self.fecha_vencimiento:
            raise ValidationError("La Fecha de Vencimiento de la Prórroga debe ser posterior a la Fecha de Vencimiento Primitiva.")
        if self.fecha_vencimiento_prorroga <= self.create_date.date():
            raise ValidationError("La Fecha de Vencimiento de la Prórroga debe ser posterior a la fecha en de Comunicación.")
        else: 
            # self.communicate_prorroga_to_api(riesgo)
            self.send_mail_doc_pago(riesgo)

            
            # Creamos la Prórroga asociado a la factura y al perfil de riesgo
            prorroga = self.env['riesgo.prorroga'].create({
                'riesgo_id': riesgo_id,
                'vencimiento_ids': vencimiento_ids,
                'importe_prorrogado': self.importe_prorrogado,
                'fecha_vencimiento': self.fecha_vencimiento,
                'fecha_vencimiento_prorroga': self.fecha_vencimiento_prorroga,
                'documento_pago': self.documento_pago,
                'documento_pago_nombre': self.documento_pago_nombre,
                'fecha_comunicacion': fields.Date.today(),
                'observacion': self.observacion,
                'estado': 'Pendiente',
                'status': 'Pendiente de Comunicar',
            })

            if self.vencimiento_ids.estado_prorroga == 'no comunicada':
                estado_prorroga = 'prorroga comunicada'
            elif self.vencimiento_ids.estado_prorroga == 'prorroga comunicada':
                estado_prorroga = 'segunda prorroga comunicada'
            elif self.vencimiento_ids.estado_prorroga == 'segunda prorroga comunicada':
                estado_prorroga = 'prorroga especial comunicada'
            elif self.vencimiento_ids.estado_prorroga == 'prorroga especial comunicada':
                raise UserError("Ya se han comunicado 3 prórrogas sobre este cobro, no puede comunicar más.")

            vencimientos.write({
                'prorroga_ids': [(4, prorroga.id)],  # Agrega la Prórroga a la relación Many2many
                'estado_prorroga': estado_prorroga,
                'date_maturity': self.fecha_vencimiento_prorroga
            })
            
            return {'type': 'ir.actions.act_window_close'}

    def communicate_prorroga_to_api(self, riesgo):
        client_id = 'CRISCOLOR'  
        url = f'http://api:5003/api/v1/{client_id}/communicate_prorroga' 
        headers = {'Content-Type': 'application/json'}

        fecha_vencimiento_str = self.fecha_vencimiento.strftime('%Y-%m-%d')
        fecha_vencimiento_prorroga_str = self.fecha_vencimiento_prorroga.strftime('%Y-%m-%d')

        payload = {
            "importe_prorrogado":  self.importe_prorrogado,
            "fecha_vencimiento": fecha_vencimiento_str,
            "fecha_vencimiento_prorroga": fecha_vencimiento_prorroga_str,

            "vat": riesgo.vat,
            "razon_social": riesgo.name,
            "country": riesgo.country_id.name if riesgo.country_id else '',
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                pass
            else:
                raise UserError(f"Error '{response.status_code}'. Comuníquese con Tecletes.")
        except requests.exceptions.RequestException as e:
            raise UserError(f"Error: '{str(e)}'. Comuníquese con Tecletes.")

    def send_mail_doc_pago(self, riesgo):
        # Obtener el correo del agente asegurador desde la configuración
        email_to = self.env['ir.config_parameter'].sudo().get_param('credito_caucion.email_agente_asegurador')
    
        # Verificar si el correo está configurado
        if not email_to:
            raise UserError("El correo del agente asegurador no está configurado en los ajustes de la aplicación.") 
        subject = 'Comunicación Prórroga'
        body = (
            f"Hola Rosana,<br><br>"
            f'Te adjunto el Documento de Pago del Cliente {riesgo.name} con NIF {riesgo.vat} para la Prórroga que acabamos de comunicar de importe {self.importe_prorrogado} para la nueva fecha de vencimiento {self.fecha_vencimiento_prorroga}.<br><br>'
            f"Saludos."
        )
        self.documento_pago_nombre = f'PRORROGA_{riesgo.vat}_{self.fecha_vencimiento_prorroga}'
        try:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'attachment_ids': [(0, 0, {
                    'name': self.documento_pago_nombre,
                    'datas': self.documento_pago,
                    'type': 'binary',
                    'res_model': 'mail.compose.message',
                })],
            }
            mail = riesgo.env['mail.mail'].create(mail_values)
            mail.send()
        except Exception as e:
            raise UserError(f"Failed to send email: {str(e)}")
