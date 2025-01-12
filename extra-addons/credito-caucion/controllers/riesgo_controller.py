from odoo import http
from odoo.http import request

class RiesgoController(http.Controller):

    # DASHBOARD 1

    @http.route('/riesgo/clasificacion_distribucion', type='json', auth='user')
    def get_clasificacion_distribucion(self):
        datos = request.env['riesgo'].get_clasificacion_distribucion()
        return {'data': datos}

    # DASHBOARD 2

    @http.route('/riesgo/incidencias_cobro', type='json', auth='user')
    def get_incidencias_cobro(self):
        datos = request.env['riesgo'].get_incidencias_cobro()
        return datos

    # DASHBOARD 3

    @http.route('/riesgo/calidad_cartera', type='json', auth='user')
    def get_calidad_cartera(self):
        riesgo_categorias = request.env['riesgo'].calcular_riesgo_clientes()
        return {'data': riesgo_categorias}

    # DASHBOARD 4

    @http.route('/riesgo/top_clasificaciones', type='json', auth='user')
    def top_clasificaciones(self):
        # Buscar y ordenar riesgos por importe concedido, de mayor a menor
        riesgos = request.env['riesgo'].search([], order='importe_concedido desc', limit=10)
        
        # Preparar los datos para el gráfico
        data = []
        for riesgo in riesgos:
            data.append({
                'cliente': riesgo.name,
                'importe_concedido': riesgo.importe_concedido,
            })
        
        # Asegurarse de enviar los datos ordenados
        data = sorted(data, key=lambda x: x['importe_concedido'], reverse=True)

        return {'result': data}