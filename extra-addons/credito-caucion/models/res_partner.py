from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'  

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade')

    _sql_constraints = [
        ('unique_riesgo', 'unique(riesgo_id)', 'Each riesgo record can only be linked to one partner.')
    ]

    @api.model
    def create(self, vals_list):
        # Asegurarse de que vals_list siempre sea una lista
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        partners = super(ResPartner, self).create(vals_list)
        for partner in partners:
            if partner.is_company:
                # Crear el perfil de riesgo asociado al partner
                riesgo = self.env['riesgo'].create({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'vat': partner.vat,
                    'country_id': partner.country_id.id})
                # Asignar el riesgo recién creado al campo riesgo_id del partner
                partner.riesgo_id = riesgo.id
        return partners

    def unlink(self):
        for partner in self:
            # Verificar si el contacto tiene un perfil de riesgo asociado
            riesgo = self.env['riesgo'].search([('partner_id', '=', partner.id)])
            if riesgo:
                # Verificar AFPs en estado "Comunicado"
                afp_comunicado = riesgo.riesgo_afp_ids.filtered(lambda afp: afp.estado == 'Comunicado')
                if afp_comunicado:
                    raise UserError("No se puede eliminar el contacto porque tiene AFPs en estado 'Comunicado'.")

                # Verificar Prórrogas en estado "Comunicada"
                prorroga_comunicada = riesgo.riesgo_prorroga_ids.filtered(lambda prorroga: prorroga.estado == 'Comunicada')
                if prorroga_comunicada:
                    raise UserError("No se puede eliminar el contacto porque tiene Prórrogas en estado 'Comunicada'.")

                # Eliminar clasificaciones si las tiene
                if riesgo.clasificacion_en_vigor:
                    for clasificacion in riesgo.clasificacion_en_vigor:
                        # Llamar a la función delete_classification_to_api antes de eliminar la clasificación
                        clasificacion.delete_classification_to_api()
                        clasificacion.unlink()

        # Si no hay restricciones, proceder con la eliminación
        return super(ResPartner, self).unlink()