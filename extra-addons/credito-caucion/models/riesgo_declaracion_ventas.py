from odoo import models, fields, api
from odoo.exceptions import UserError

import requests


class RiesgoDeclaracionVentas(models.Model):
    _name = 'riesgo.declaracion.ventas'
    _description = 'Declaración de Ventas por Mes y Año'

    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('declarada', 'Declarada'),
    ], string='Estado', default='borrador')
    mes = fields.Selection([
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'),
        ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
        ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'),
        ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ], string='Mes', required=True)

    ano = fields.Integer(string='Año', required=True)

    # Campos agregados de importes totales
    total_ventas_asegurables = fields.Float(string='Total Ventas Asegurables', compute='_compute_totales', store=True)
    total_ventas_no_asegurables = fields.Float(string='Total Ventas No Asegurables', compute='_compute_totales', store=True)
    total_ventas = fields.Float(string='Total Ventas', compute='_compute_totales', store=True)

    # Relación con las ventas asegurables y no asegurables
    ventas_asegurables_ids = fields.One2many('riesgo.ventas.asegurables', 'declaracion_id', string='Ventas Asegurables')
    ventas_no_asegurables_ids = fields.One2many('riesgo.ventas.noasegurables', 'declaracion_id', string='Ventas No Asegurables')

    # Estado de la declaración
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('declarado', 'Declarado')
    ], string='Estado', default='pendiente')

    @api.depends('ventas_asegurables_ids.importe', 'ventas_no_asegurables_ids.importe')
    def _compute_totales(self):
        """Calcula los totales de ventas asegurables y no asegurables"""
        for record in self:
            record.total_ventas_asegurables = sum(linea.importe for linea in record.ventas_asegurables_ids)
            record.total_ventas_no_asegurables = sum(linea.importe for linea in record.ventas_no_asegurables_ids)
            record.total_ventas = record.total_ventas_asegurables + record.total_ventas_no_asegurables


    def action_declarar(self):
        self.declarar_ventas_to_api()
        for record in self:
            record.estado = 'declarado'

    def declarar_ventas_to_api(self):
        client_id = 'CRISCOLOR'  
        url = f'http://api:5003/api/v1/{client_id}/declaracions_ventas' 
        headers = {'Content-Type': 'application/json'}
        
        # Datos asegurables
        ventas_asegurables = []
        for venta in self.ventas_asegurables_ids:
            ventas_asegurables.append({
                "pais": venta.pais,
                "duracion": venta.duracion,  # Aquí se puede mapear a los valores numéricos (30, 60, 90, etc.)
                "importe": venta.importe
            })
        
        # Datos no asegurables
        ventas_no_asegurables = []
        for venta in self.ventas_no_asegurables_ids:
            ventas_no_asegurables.append({
                "tipo_cliente": venta.tipo_cliente,  # naturalezaClienteInterior o naturalezaClienteExterior
                "importe": venta.importe
            })

        # Payload para la API
        payload = {
            "mes": self.mes,
            "ano": self.ano,
            "importe_ventas": self.total_ventas_asegurables + self.total_ventas_no_asegurables,  # Suma de asegurables y no asegurables
            "total_ventas_aseguradas": self.total_ventas_asegurables,  # Total asegurables
            "total_ventas_noaseguradas": self.total_ventas_no_asegurables,  # Total no asegurables
            "ventas_asegurables": ventas_asegurables,  # Detalle de ventas asegurables
            "ventas_no_asegurables": ventas_no_asegurables  # Detalle de ventas no asegurables
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                pass
            else:
                raise UserError(f"Error '{response.status_code}'. Comuníquese con Tecletes.")
        except requests.exceptions.RequestException as e:
            raise UserError(f"Error: '{str(e)}'. Comuníquese con Tecletes.")


class RiesgoVentasAsegurables(models.Model):
    _name = 'riesgo.ventas.asegurables'
    _description = 'Ventas Asegurables Detalladas'
    _order = 'orden_pais asc, pais asc'

    declaracion_id = fields.Many2one('riesgo.declaracion.ventas', string='Declaración', required=True, ondelete='cascade')
    pais = fields.Char(string='País', required=True)
    importe = fields.Float(string='Importe', required=True)
    duracion = fields.Selection([
        ('30', '30 días'),
        ('60', '60 días'),
        ('90', '90 días'),
        ('120', '120 días')
    ], string='Duración', required=True)
    
    orden_pais = fields.Integer(string="Orden País", compute="_compute_orden_pais")

    @api.depends('pais')
    def _compute_orden_pais(self):
        for record in self:
            # Si el país es España, se asigna el valor más bajo
            if record.pais == 'España':
                record.orden_pais = 1
            else:
                record.orden_pais = 2  # Otros países tendrán un valor mayor


class RiesgoVentasNoAsegurables(models.Model):
    _name = 'riesgo.ventas.noasegurables'
    _description = 'Ventas No Asegurables Detalladas'

    declaracion_id = fields.Many2one('riesgo.declaracion.ventas', string='Declaración', required=True, ondelete='cascade')
    tipo_cliente = fields.Selection([
        ('cliente_tipo_1', 'Tipo Cliente 1'),
        ('cliente_tipo_2', 'Tipo Cliente 2'),
        ('cliente_tipo_3', 'Tipo Cliente 3')
    ], string='Tipo de Cliente', required=True)
    importe = fields.Float(string='Importe', required=True)
