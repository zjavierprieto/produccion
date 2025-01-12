from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        # Llamar al método original para mantener la funcionalidad existente
        result = super(AccountPaymentRegister, self).action_create_payments()

        # Obtener las facturas asociadas a las líneas contables
        moves = self.line_ids.mapped('move_id')

        # Verificar si las facturas están completamente pagadas
        for move in moves:
            if move.payment_state == 'paid':
                # Si está completamente pagado, cancelar AFP, prórroga o siniestro
                #move._cancel_afp_prorroga_siniestro()
                pass
        # Devolver el resultado del método original
        return result
