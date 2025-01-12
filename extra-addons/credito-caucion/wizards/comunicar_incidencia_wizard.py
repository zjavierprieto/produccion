from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)

class ComunicarIncidenciaWizard(models.TransientModel):
    _name = 'comunicar.incidencia.wizard'
    _description = 'Wizard para comunicar incidencia'

    vencimiento_ids = fields.Many2many('account.move.line', string='Vencimientos', readonly=True)
    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete="cascade")

    importe_impagado = fields.Float(string='Importe Impagado', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', required=True)

    def action_abrir_wizard_afp(self):
        _logger.info(self.riesgo_id.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.riesgo.afp',
            'name': 'Comunicar AFP',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vencimiento_ids': self.vencimiento_ids.ids,
                'default_riesgo_id': self.riesgo_id.id, 
                'default_importe_impagado': self.importe_impagado, 
                'default_fecha_vencimiento': self.fecha_vencimiento,
            }
        }

    def action_abrir_wizard_prorroga(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.riesgo.prorroga',
            'name': 'Comunicar Prórroga',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vencimiento_ids': self.vencimiento_ids.ids,
                'default_riesgo_id': self.riesgo_id.id, 
                'default_importe_prorrogado': self.importe_impagado, 
                'default_fecha_vencimiento': self.fecha_vencimiento,
            }
        }

    def action_abrir_wizard_siniestro(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.riesgo.siniestro',
            'name': 'Declarar Siniestro',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vencimiento_ids': self.vencimiento_ids.ids,
                'default_riesgo_id': self.riesgo_id.id, 
                'default_credito_total': self.importe_impagado, 
                'default_fecha_impago': self.fecha_vencimiento,
            }
        }
