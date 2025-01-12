from odoo import http
from odoo.http import request

class VencimientosController(http.Controller):

    # DASHBOARD 1

    @http.route('/vencimientos/ventas_cobros', type='json', auth='user')
    def get_ventas_cobros_dinamicos(self):
        datos = request.env['account.move.line'].get_ventas_cobros_dinamicos()
        return {
            'labels': datos['labels'],
            'facturacion': datos['facturacion'],
            'cobros': datos['cobros'],
            'saldo_vencimientos': datos['saldo_vencimientos'],
            'deuda_fuera_plazo': datos['deuda_fuera_plazo']
        }
    
    # DASHBOARD 2

    @http.route('/vencimientos/saldo_facturas', type='json', auth='user')
    def get_saldo_vencimientos(self):
        datos = request.env['account.move.line'].get_saldo_vencimientos()
        return {'labels': datos['labels'], 'datasets': datos['datasets']}

    # DASHBOARD 3

    @http.route('/vencimientos/proximos_cobros', type='json', auth='user')
    def get_proximos_vencimientos(self):
        datos = request.env['account.move.line'].get_proximos_vencimientos()
        return {'labels': datos['labels'], 'datasets': datos['datasets']}

    # DASHBOARD 4

    @http.route('/vencimientos/top_10_customers_impagadas', type='json', auth='user')
    def top_10_customers_impagadas(self):
        # Llamamos a la función del modelo que obtiene los datos
        data = request.env['account.move.line'].get_top_10_customers_impagadas()
        return data