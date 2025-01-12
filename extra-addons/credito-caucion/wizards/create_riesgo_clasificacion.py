from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import requests


class CreateRiesgoClasificacion(models.TransientModel):
    _name = 'create.riesgo.clasificacion'
    _description = 'Wizard para crear, ampliar, reducir o eliminar una clasificación de riesgo'

    importe_concedido = fields.Float(string='Cobertura Actual')
    importe_solicitado = fields.Float(string='Importe Solicitado', required=True)
    action_type = fields.Selection([
        ('clasificar', 'Clasificar'),
        ('ampliar', 'Ampliar'),
        ('reducir', 'Reducir'),
        ('eliminar', 'Eliminar')
    ], string="Tipo de Acción", readonly=True, default=lambda self: self.env.context.get('default_action_type'))

    # -----------------------
    # Seleccionador de Acción 
    # -----------------------

    def action_submit(self):
        riesgo_id = self.env.context.get('default_riesgo_id')
        if not riesgo_id:
            raise UserError("No se ha especificado el riesgo.")
        
        riesgo = self.env['riesgo'].browse(riesgo_id)
        if not riesgo.exists():
            raise UserError("El registro de Riesgo no existe.")
        
        if not self.importe_solicitado:
            raise ValidationError("Por favor, complete el Importe Solicitado.")

        # Acción según el tipo de acción
        if self.action_type == 'clasificar':
            self.send_classification_request_to_api(riesgo)
            self._crear_clasificacion(riesgo)
            riesgo.estado_clasificacion = 'pendiente'
        elif self.action_type == 'ampliar':
            self.send_classification_request_to_api(riesgo)
            self._ampliar_clasificacion(riesgo)
            riesgo.estado_clasificacion = 'pendiente'
        elif self.action_type == 'reducir':
            self.send_classification_request_to_api(riesgo)
            self._reducir_clasificacion(riesgo)
            riesgo.estado_clasificacion = 'pendiente'
        elif self.action_type == 'eliminar':
            self.send_classification_request_to_api(riesgo)
            self._eliminar_clasificacion(riesgo)
            riesgo.estado_clasificacion = 'pendiente'

        return {'type': 'ir.actions.act_window_close'}

    # -----------------
    # Acciones Posibles 
    # -----------------

    def _crear_clasificacion(self, riesgo):
        self.env['riesgo.clasificacion'].create({
            'riesgo_id': riesgo.id,
            'importe_solicitado': self.importe_solicitado,
            'fecha_solicitud':  fields.Date.today(),
            'estado': 'Pendiente',
            'status': 'Pendiente de Validar',
        })

    def _ampliar_clasificacion(self, riesgo):
        self.env['riesgo.clasificacion'].create({
            'riesgo_id': riesgo.id,
            'importe_solicitado': self.importe_solicitado,
            'fecha_solicitud':  fields.Date.today(),
            'estado': 'Pendiente',
            'status': 'Pendiente de Validar',
        })
        
    def _reducir_clasificacion(self, riesgo):
        self.env['riesgo.clasificacion'].create({
            'riesgo_id': riesgo.id,
            'importe_solicitado': self.importe_solicitado,
            'fecha_solicitud':  fields.Date.today(),
            'estado': 'Pendiente',
            'status': 'Pendiente de Validar',
        })
        self.send_reduccion_request_to_mail(riesgo)

    def _eliminar_clasificacion(self, riesgo):
        # Buscar la clasificación actual en vigor
        clasificacion_vigente = self.env['riesgo.clasificacion'].search([
            ('riesgo_id', '=', riesgo.id),
            ('estado', '=', 'En Vigor')  # Asegurarse de buscar la clasificación en vigor
        ], limit=1)

        # Verificar si se encontró una clasificación en vigor
        if not clasificacion_vigente:
            raise UserError(_("No se encontró ninguna clasificación en vigor para este riesgo."))

        # Llamar a la función eliminar_clasificacion en el modelo riesgo.clasificacion
        self.send_eliminacion_request_to_mail(riesgo)
        clasificacion_vigente.eliminar_clasificacion()

    # ----------------------
    # Comunicaciones vía API
    # ----------------------

    def send_classification_request_to_api(self, riesgo):
            client_id = 'CRISCOLOR'  
            url = f'http://api:5003/api/v1/{client_id}/classification_request' 
            headers = {'Content-Type': 'application/json'}
            payload = {
                "importe_solicitado": self.importe_solicitado,
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

    # -----------------------
    # Comunicaciones vía MAIL
    # -----------------------

    def send_reduccion_request_to_mail(self, riesgo):
        email_to = 'zjavierprieto@gmail.com'  
        subject = 'Reducción de Clasificación'
        body = (
            f"Hola Rosana,<br><br>"
            f"Me gustaría que me redujeras la clasificación sobre el siguiente cliente:<br><br>"
            f"NIF: {riesgo.vat},<br>"
            f"Razón Social: {riesgo.name},<br>"
            f"Reducción solicitada: {self.importe_solicitado}.<br><br>"

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

    def send_eliminacion_request_to_mail(self, riesgo):
        email_to = 'zjavierprieto@gmail.com'  
        subject = 'Eliminación de Clasificación'
        body = (
            f"Hola Rosana,<br><br>"
            f"Me gustaría que me eliminaras la clasificación sobre el siguiente cliente:<br><br>"
            
            f"NIF: {riesgo.vat},<br>"
            f"Razón Social: {riesgo.name},<br><br>"

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



