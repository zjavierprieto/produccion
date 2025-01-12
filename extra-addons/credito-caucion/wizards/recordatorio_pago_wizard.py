from odoo import models, fields, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class RecordatorioPagoWizard(models.TransientModel):
    _name = 'recordatorio.pago.wizard'
    _description = 'Recordatorio Pago Wizard'

    vencimiento_id = fields.Many2one('account.move.line', string="Vencimiento", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Destinatario", required=True)
    subject = fields.Char(string="Asunto", default="Recordatorio de Pago")
    body = fields.Text(string="Mensaje", default=lambda self: self._default_body())
    attachment_ids = fields.Many2many('ir.attachment', string="Archivos adjuntos")

    @api.model
    def _default_body(self):
        vencimiento = self.env.context.get('default_vencimiento_id')
        if not vencimiento:
            return "Error: No se pudo obtener el vencimiento pendiente."

        vencimiento_record = self.env['account.move.line'].browse(vencimiento)

        # Generar el cuerpo del mensaje para el vencimiento
        vencimiento_texto = (
            f"- Factura {vencimiento_record.move_id.name}, Importe: {vencimiento_record.amount_residual:.2f}, "
            f"Fecha de vencimiento: {vencimiento_record.date_maturity}"
        )

        return (
            f"Estimado cliente,\n\n"
            f"Le recordamos que tiene el siguiente vencimiento pendiente:\n\n"
            f"{vencimiento_texto}\n\n"
            f"Por favor, póngase en contacto con nosotros si tiene alguna pregunta.\n\n"
            f"Gracias."
        )

    def send_reminder(self):
        email_to = self.partner_id.email

        # Comprobar si el email está disponible
        if not email_to:
            raise UserError("No se ha encontrado un correo electrónico asociado al perfil del cliente.")

        # Convertir el cuerpo del mensaje a HTML
        body_html = self.body.replace("\n", "<br>")

        # Enviar el correo con el cuerpo ya construido
        mail_values = {
            'subject': self.subject,
            'body_html': f"<p>{body_html}</p>",
            'email_to': email_to,
            'attachment_ids': [(6, 0, self.attachment_ids.ids)]
        }

        try:
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

            if self.vencimiento_id.estado_prorroga == 'no comunicada':
                estado_recordatorio_pago = 'recordatorio de pago enviado'
            elif self.vencimiento_id.estado_prorroga == 'prorroga comunicada':
                estado_recordatorio_pago = 'recordatorio de pago prorroga 1 enviado'
            elif self.vencimiento_id.estado_prorroga == 'segunda prorroga comunicada':
                estado_recordatorio_pago = 'recordatorio de pago prorroga 2 enviado'
            elif self.vencimiento_id.estado_prorroga == 'prorroga especial comunicada':
                estado_recordatorio_pago = 'recordatorio de pago prorroga especial enviado'

            # Marcar el vencimiento como recordatorio enviado
            self.vencimiento_id.write({
                'estado_recordatorio_pago': estado_recordatorio_pago,
                'fecha_recordatorio': fields.Datetime.now(),
            })

        except Exception as e:
            raise UserError(f"Error al enviar el recordatorio: {str(e)}")

        return {'type': 'ir.actions.act_window_close'}

