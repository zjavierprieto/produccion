from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ------------------
    # ALERTA INCIDENCIAS 
    # ------------------

    # Alerta al introducir cliente en presupuesto

    @api.onchange('partner_id')
    def _onchange_partner_check_risk(self):
        if self.partner_id:
            # Acceder a los registros de AFP, Prórroga y Siniestro relacionados con el cliente
            afps = self.env['riesgo.afp'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Comunicado')])
            prorrogas = self.env['riesgo.prorroga'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Comunicada')])
            siniestros = self.env['riesgo.siniestro'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Abierto')])

            # Mensajes personalizados según el tipo de incidencia
            mensaje_alerta = ""
            if afps:
                mensaje_alerta += _("El cliente tiene AFPs comunicados. \n")
            if prorrogas:
                mensaje_alerta += _("El cliente tiene Prórrogas comunicadas. \n")
            if siniestros:
                mensaje_alerta += _("El cliente tiene Siniestros abiertos. \n")

            # Si hay alguna incidencia, mostrar el warning
            if mensaje_alerta:
                warning = {
                    'title': _("Advertencia: Riesgo Detectado"),
                    'message': ("\n") + mensaje_alerta + _("Por favor, proceda con precaución."),
                }
                return {'warning': warning}

    # Alerta al confirmar presupuesto -> pedido de venta
    
    def action_confirm(self):
        # Verificar si el chequeo de incidencias debe saltarse (para evitar recursión)
        if self.env.context.get('skip_incidence_check'):
            return super(SaleOrder, self).action_confirm()

        # Verificar si el cliente tiene incidencias abiertas
        afps = self.env['riesgo.afp'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Comunicado')])
        prorrogas = self.env['riesgo.prorroga'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Comunicada')])
        siniestros = self.env['riesgo.siniestro'].search([('riesgo_id', '=', self.partner_id.riesgo_id.id), ('estado', '=', 'Abierto')])

        # Si hay incidencias abiertas, lanzar un confirm dialog
        if afps or prorrogas or siniestros:
            mensaje_alerta = ""
            if afps:
                mensaje_alerta += _("El cliente tiene AFPs comunicados. ")
            if prorrogas:
                mensaje_alerta += _("El cliente tiene Prórrogas comunicadas. ")
            if siniestros:
                mensaje_alerta += _("El cliente tiene Siniestros abiertos. ")

            mensaje_alerta += _("\n\nRecuerde que el cliente no está asegurado. ¿Está seguro de confirmar el pedido de venta?")

            # Lanzar una ventana de confirmación
            return {
                'name': _("Confirmación de Riesgo"),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order.confirm.warning',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {
                    'default_sale_order_id': self.id,
                    'default_message': mensaje_alerta,
                    'default_action': 'confirm',
                }
            }

        # Verificar si el cliente tiene clasificación de riesgo
        riesgo = self.partner_id.riesgo_id

        if not riesgo or not riesgo.importe_concedido:
            mensaje_alerta = _("El cliente no tiene clasificación. Sugerimos solicitar una clasificación.")
            importe_recomendado = round(self.amount_total / 1000.0) * 1000
        else:
            # Comparar el importe total del pedido con el importe concedido
            if self.amount_total > riesgo.importe_concedido:
                mensaje_alerta = _("El importe total del pedido excede la clasificación concedida. Sugerimos solicitar una ampliación.")
                importe_recomendado = round(self.amount_total / 1000.0) * 1000
            else:
                # Calcular el saldo vivo del cliente
                saldo_vivo_total = self.calcular_saldo_vivo(self.partner_id.id)

                # Redondear el saldo vivo hacia arriba en miles de euros
                importe_recomendado = round(saldo_vivo_total / 1000.0) * 1000

                if saldo_vivo_total > riesgo.importe_concedido:
                    mensaje_alerta = _("El saldo vivo (facturas + pedidos no facturados) excede la clasificación del cliente. Sugerimos solicitar una ampliación.")
                else:
                    # Si todo está bien, proceder normalmente
                    return super(SaleOrder, self).action_confirm()

        # Lanzar una ventana de advertencia si hay problemas con la clasificación
        return {
            'name': _("Advertencia de Clasificación"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.confirm.warning',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_message': mensaje_alerta,
                'default_action': 'confirm',
                'default_importe_solicitado': importe_recomendado,
                'default_riesgo_id': self.partner_id.riesgo_id.id,
                'default_tipo_solicitud': 'ampliacion',
            }
        }

    # -------------------
    # CALCULAR SALDO VIVO 
    # -------------------

    def calcular_saldo_vivo(self, partner_id):
        """ Calcula el saldo vivo de un cliente.
        
        Suma las facturas no pagadas o parcialmente pagadas (amount_residual) y los pedidos confirmados o realizados que aún no están completamente facturados (amount_total).
        
        :param partner_id: ID del cliente para el cual calcular el saldo vivo
        :return: saldo_vivo_total (facturas + pedidos no facturados)
        """
        # Obtener facturas pendientes de pago
        facturas_pendientes = self.env['account.move'].search([
            ('partner_id', '=', partner_id),
            ('move_type', '=', 'out_invoice'),  # Solo facturas de venta
            ('payment_state', 'not in', ['paid', 'in_payment'])  # Facturas no pagadas o parcialmente pagadas
        ])
        saldo_vivo_facturas = sum(factura.amount_residual for factura in facturas_pendientes)

        # Obtener pedidos que no han sido completamente facturados
        pedidos_abiertos = self.env['sale.order'].search([
            ('partner_id', '=', partner_id),
            ('state', 'in', ['sale', 'done']),  # Pedidos confirmados o realizados
            ('invoice_status', '!=', 'invoiced')  # Pedidos no completamente facturados
        ])
        saldo_vivo_pedidos = sum(pedido.amount_total for pedido in pedidos_abiertos)

        # Calcular el saldo vivo total
        saldo_vivo_total = saldo_vivo_facturas + saldo_vivo_pedidos

        return saldo_vivo_total
