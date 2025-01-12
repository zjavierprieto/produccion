from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

import requests

class CreateRiesgoAfp(models.TransientModel):
    _name = 'create.riesgo.afp'
    _description = 'Wizard para crear un AFP'

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos Asociados', required=True)

    importe_impagado = fields.Float(string='Importe Impagado', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', required=True)
    observacion = fields.Char(string='Observación')
  
    def action_create_afp(self):
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

        if not self.importe_impagado:
            raise ValidationError("Por favor, complete el Importe Impagado.")
        if not self.fecha_vencimiento:
            raise ValidationError("Por favor, complete la Fecha de Vencimiento.") 
        else: 
            # Crear el AFP asociado a los vencimientos y al perfil de riesgo
            afp = self.env['riesgo.afp'].create({
                'riesgo_id': riesgo_id,
                'vencimiento_ids': [(6, 0, vencimientos.ids)],
                'importe_impagado': self.importe_impagado,
                'fecha_vencimiento': self.fecha_vencimiento,
                'fecha_comunicacion': fields.Date.today(),
                'observacion': self.observacion,
                'estado': 'Pendiente',
                'status': 'Pendiente de Comunicar',
            })

            if self.vencimiento_ids.estado_prorroga == 'no comunicada':
                estado_afp = 'afp comunicado'
            elif self.vencimiento_ids.estado_prorroga == 'prorroga comunicada':
                estado_afp = 'afp prorroga 1 comunicado'
            elif self.vencimiento_ids.estado_prorroga == 'segunda prorroga comunicada':
                estado_afp = 'afp prorroga 2 comunicado'
            elif self.vencimiento_ids.estado_prorroga == 'prorroga especial comunicada':
                raise UserError("Ya se han comunicado 3 prórrogas sobre este cobro, no puede comunicar otro AFP.")

            vencimientos.write({
                'afp_ids': [(4, afp.id)],  # Agrega el AFP a la relación Many2many
                'estado_afp': estado_afp,
            })
            
            return {'type': 'ir.actions.act_window_close'}

    def communicate_afp_to_api(self, riesgo):
        client_id = 'CRISCOLOR'  
        url = f'http://api:5003/api/v1/{client_id}/communicate_afp' 
        headers = {'Content-Type': 'application/json'}

        fecha_vencimiento_str = self.fecha_vencimiento.strftime('%Y-%m-%d')

        payload = {
            "importe_impagado":  self.importe_impagado,
            "fecha_vencimiento": fecha_vencimiento_str,

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

 