from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import requests

class CreateRiesgoSiniestro(models.TransientModel):
    _name = 'create.riesgo.siniestro'
    _description = 'Wizard para comunicar un Siniestro'

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos Asociados', required=True)
    credito_total = fields.Float(string='Crédito Total', required=True)
    fecha_impago = fields.Date(string='Fecha Impago', required=True)
    observacion = fields.Char(string='Observación')
    documentos_ids = fields.Many2many(
        'ir.attachment',
        string="Documentos",
        required=True,
        help="Adjuntar todos los documentos relacionados con el impago. (Facturas, Albaranes, Pagarés, Certificados de Entrega, Recibos devueltos, Si es Exterior el BL...)"
    )

    def action_create_siniestro(self):
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

        if not self.documentos_ids:
            raise ValidationError('Debe adjuntar los documentos correspondientes al sinestro.')
        if not self.credito_total:
            raise ValidationError("Por favor, complete el Importe siniestrado.")
        if not self.fecha_impago:
            raise ValidationError("Por favor, complete la Fecha de Impago.")
        else:       
            # Creamos el Siniestro asociado a la factura y al perfil de riesgo
            siniestro = self.env['riesgo.siniestro'].create({
                'riesgo_id': riesgo_id,
                'vencimiento_ids': vencimiento_ids,
                'credito_total': self.credito_total,
                'fecha_impago': self.fecha_impago,
                'documentos_ids': self.documentos_ids,
                'fecha_comunicacion': fields.Date.today(),
                'estado': 'Pendiente',
            })

            vencimientos.write({
                'siniestro_ids': [(4, siniestro.id)],  # Agrega el Siniestro a la relación Many2many
                'estado_siniestro': 'siniestro declarado',
            })
            
            self.send_mail_siniestro(riesgo)
            return {'type': 'ir.actions.act_window_close'}

    def send_mail_siniestro(self, riesgo):
        # Obtener el correo del agente asegurador desde la configuración
        email_to = self.env['ir.config_parameter'].sudo().get_param('credito_caucion.email_agente_asegurador')
    
        # Verificar si el correo está configurado
        if not email_to:
            raise UserError("El correo del agente asegurador no está configurado en los ajustes de la aplicación.")
    
        subject = 'Siniestro'
        body = (
            f"Hola Rosana,<br><br>"
            f"Me gustaría que me declararas un siniestro sobre el siguiente cliente:<br><br>"
            f"NIF: {riesgo.vat},<br>"
            f"Razón Social: {riesgo.name},<br>"
            f"Crédito Total: {self.credito_total},<br>"
            f"Fecha de Impago: {self.fecha_impago}.<br><br>"

            f"Te adjunto los documentos que tengo, en caso de necesitar alguno más no dudes en pedirmelos.<br><br>"
            f"Muchas gracias,<br>"
            f"Saludos."
        )

        try:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'attachment_ids': [(6, 0, self.documentos_ids.ids)],
            }
            mail = riesgo.env['mail.mail'].create(mail_values)
            mail.send()
        except Exception as e:
            raise UserError(f"Failed to send email: {str(e)}")
