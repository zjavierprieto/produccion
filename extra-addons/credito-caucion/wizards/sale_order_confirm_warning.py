from odoo import models, fields, api

class SaleOrderConfirmWarning(models.TransientModel):
    _name = 'sale.order.confirm.warning'
    _description = 'Advertencia de Confirmación de Riesgo'

    message = fields.Text(string="Mensaje de Advertencia", readonly=True)

    # Confirmar presupuesto -> pedido de venta a pesar de tener incidencias
    
    def confirm_action(self):
        # Obtener la referencia a la orden de venta desde el contexto
        sale_order_id = self.env.context.get('default_sale_order_id')
        sale_order = self.env['sale.order'].browse(sale_order_id)

        # Confirmar el pedido de venta
        sale_order.with_context(skip_incidence_check=True).action_confirm()

        return {'type': 'ir.actions.act_window_close'}

    def action_solicitar_ampliacion(self):
        importe_recomendado = self.env.context.get('default_importe_recomendado')
        riesgo_id = self.env.context.get('default_riesgo_id')

        return {
            'name': 'Solicitar Ampliación de Clasificación',
            'type': 'ir.actions.act_window',
            'res_model': 'create.riesgo.clasificacion',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_importe_solicitado': importe_recomendado,  # Rellenar con el valor recomendado
                'default_riesgo_id': riesgo_id,  # Pasar el ID del riesgo
                'default_action_type': 'ampliar',  # Indicar que es una ampliación
            }
        }