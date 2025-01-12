from odoo import models, fields, api, tools
from odoo.exceptions import UserError
from odoo.tools import misc
from datetime import datetime, timedelta

import os
import base64
import logging

_logger = logging.getLogger(__name__)


class Riesgo(models.Model):
    _name = 'riesgo'
    _description = 'Riesgo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete="cascade")
    actividad_ids = fields.One2many('mail.activity', 'riesgo_id', string='Actividades')

    _sql_constraints = [
        ('unique_partner', 'unique (partner_id)', 'Each partner can have only one Riesgo record.'),
        ('unique_clasificacion_en_vigor', 'unique (clasificacion_en_vigor)', 'Each Riesgo record can have only one clasificacion en vigor.')
    ]

# --------------------------- 
# Related Fields (res.partner)
# ---------------------------

    # Required Fields

    name = fields.Char(related='partner_id.name', store=True, readonly=False)
    vat = fields.Char(related='partner_id.vat', store=True, readonly=False)
    country_id = fields.Many2one(related='partner_id.country_id', store=True, readonly=False)
    
    # Optional Fields

    street = fields.Char(related='partner_id.street', store=True, readonly=False)
    city = fields.Char(related='partner_id.city', store=True, readonly=False)
    zip = fields.Char(related='partner_id.zip', store=True, readonly=False)
    state_id = fields.Many2one(related='partner_id.state_id', store=True, readonly=False)
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False)
    mail = fields.Char(related='partner_id.email', store=True, readonly=False)
    website = fields.Char(related='partner_id.website', store=True, readonly=False)
    image_128 = fields.Image(related='partner_id.avatar_128', store=True, readonly=False)

    # -----------
    # Risk Fields
    # -----------

    expediente = fields.Integer(string='Expediente', store=True)
    cnae = fields.Char(string='CNAE', store=True)
    clasificado_bool = fields.Boolean(string='Cliente Casificado', compute="_compute_clasificaciones", store=True)

    # ----------------------
    # Sub-Models Definitions
    # ----------------------

    riesgo_clasificacion_ids = fields.One2many('riesgo.clasificacion', 'riesgo_id', string='Clasificaciones')
    riesgo_afp_ids = fields.One2many('riesgo.afp', 'riesgo_id', string='AFPs')
    riesgo_prorroga_ids = fields.One2many('riesgo.prorroga', 'riesgo_id', string='Prórrogas')
    riesgo_siniestro_ids = fields.One2many('riesgo.siniestro', 'riesgo_id', string='Siniestros')
    riesgo_alerta_ids = fields.One2many('riesgo.alerta', 'riesgo_id', string='Alertas')
    riesgo_resultado_ids = fields.One2many('riesgo.resultado', 'riesgo_id', string='Resultados')

# --------------------------------
# Counter Fields (tarjetas kanban)
# --------------------------------

    @api.depends('afp_comunicados.importe_impagado', 'prorrogas_comunicadas.importe_prorrogado', 'siniestros_abiertos.credito_total', 'alertas_nuevas.descripcion')
    def _compute_campos_kanban(self):
        for record in self:
            
            record.numero_afp_comunicados = len(record.afp_comunicados)
            record.importe_total_afp_comunicados = sum(record.afp_comunicados.mapped('importe_impagado') or [0])

            
            record.numero_prorrogas_comunicadas = len(record.prorrogas_comunicadas)
            record.importe_total_prorrogas_comunicadas = sum(record.prorrogas_comunicadas.mapped('importe_prorrogado') or [0])

            
            record.numero_siniestros_abiertos = len(record.siniestros_abiertos)
            record.importe_total_siniestros_abiertos = sum(record.siniestros_abiertos.mapped('credito_total') or [0])

            record.numero_alertas_nuevas = len(record.alertas_nuevas)

    numero_afp_comunicados = fields.Integer(string='Número de AFPs', compute='_compute_campos_kanban')
    numero_prorrogas_comunicadas = fields.Integer(string='Número de Prórrogas', compute='_compute_campos_kanban')
    numero_siniestros_abiertos = fields.Integer(string='Número de Siniestros', compute='_compute_campos_kanban')
    numero_alertas_nuevas = fields.Integer(string='Número de Alertas', compute='_compute_campos_kanban')
        
    importe_total_afp_comunicados = fields.Float(string='Importe Total de AFPs', compute='_compute_campos_kanban')
    importe_total_prorrogas_comunicadas = fields.Float(string='Importe Total de Prórrogas', compute='_compute_campos_kanban')
    importe_total_siniestros_abiertos = fields.Float(string='Importe Total de Siniestros', compute='_compute_campos_kanban')

# -------------------------
# Classification Reporting
# -------------------------

    # Definir campo Many2one para almacenar la clasificación en vigor

    clasificacion_vigor = fields.Many2one('riesgo.clasificacion', compute='_compute_clasificacion_vigor', string="Clasificación en Vigor")

    # Método para calcular la clasificación en vigor

    @api.depends('clasificacion_en_vigor')
    def _compute_clasificacion_vigor(self):
        for record in self:
            # Si hay clasificaciones en vigor, seleccionamos la primera
            record.clasificacion_vigor = record.clasificacion_en_vigor[:1]

    # Campos relacionados a la clasificación en vigor

    fecha_clasificacion = fields.Date(related='clasificacion_vigor.fecha_clasificacion', string="Fecha", readonly=True)
    importe_solicitado = fields.Float(related='clasificacion_vigor.importe_solicitado', string="Importe Solicitado", readonly=True)
    importe_concedido = fields.Float(related='clasificacion_vigor.importe_concedido', string="Importe Concedido", readonly=True)
    importe_concedido_empresa = fields.Float(related='clasificacion_vigor.importe_concedido_empresa', string="Concedido Empresa", readonly=False)
    motivo = fields.Char(related='clasificacion_vigor.motivo', string="Motivo", readonly=True)
    estado = fields.Selection(related='clasificacion_vigor.estado', string="Estado", readonly=True)

# ------------------
# Results Resporting 
# ------------------

    # Campos relacionados, sin almacenamiento en la tabla riesgo

    ejercicio = fields.Integer(related='riesgo_resultado_ids.ejercicio', string='Ejercicio', store=False)
    ventas = fields.Float(related='riesgo_resultado_ids.ventas', string='Ventas', store=False)
    resultado = fields.Float(related='riesgo_resultado_ids.resultado', string='Resultado', store=False)
    fondos_propios = fields.Float(related='riesgo_resultado_ids.fondos_propios', string='Fondos Propios', store=False)
    fondos_maniobra = fields.Float(related='riesgo_resultado_ids.fondos_maniobra', string='Fondos de Maniobra', store=False)
    endeudamiento_cp = fields.Float(related='riesgo_resultado_ids.endeudamiento_cp', string='Endeudamiento CP', store=False)
    empleados = fields.Integer(related='riesgo_resultado_ids.empleados', string='Empleados', store=False)
    descripcion_cnae = fields.Char(related='riesgo_resultado_ids.descripcion_cnae', string='Descripción CNAE', store=False)
    importe_concedido_resultados = fields.Float(related='riesgo_resultado_ids.importe_concedido', string='Importe Concedido', store=False)
    importe_solicitado_resultados = fields.Float(related='riesgo_resultado_ids.importe_solicitado', string='Importe Solicitado', store=False)
    num_afp = fields.Integer(related='riesgo_resultado_ids.num_afp', string='Número de AFPs', store=False)
    num_pro = fields.Integer(related='riesgo_resultado_ids.num_pro', string='Número de Prórrogas', store=False)
    num_sin = fields.Integer(related='riesgo_resultado_ids.num_sin', string='Número de Siniestros', store=False)

# -------------------
# Sub-models Sections
# -------------------
    
# ---------------
# Clasificaciones
# ---------------

    @api.depends('riesgo_clasificacion_ids.estado')
    def _compute_clasificaciones(self):
        for record in self:
            record.clasificacion_en_vigor = record.riesgo_clasificacion_ids.filtered(lambda c: c.estado == 'En Vigor')
            record.clasificacion_pendiente = record.riesgo_clasificacion_ids.filtered(lambda c: c.estado == 'Pendiente')
            record.clasificaciones_historico = record.riesgo_clasificacion_ids.filtered(lambda c: c.estado == 'Historico')

            record.clasificado_bool = bool(record.clasificacion_en_vigor)

    clasificacion_en_vigor = fields.One2many('riesgo.clasificacion', 'riesgo_id', compute='_compute_clasificaciones')
    clasificacion_pendiente = fields.One2many('riesgo.clasificacion', 'riesgo_id', compute='_compute_clasificaciones')
    clasificaciones_historico = fields.One2many('riesgo.clasificacion', 'riesgo_id', compute='_compute_clasificaciones')

# ----
# AFPs
# ----

    @api.depends('riesgo_afp_ids.estado')
    def _compute_afp(self):
        for record in self:
            record.afp_comunicados = record.riesgo_afp_ids.filtered(lambda c: c.estado == 'Comunicado')
            record.afp_pendientes = record.riesgo_afp_ids.filtered(lambda c: c.estado == 'Pendiente')
            record.afp_cancelados = record.riesgo_afp_ids.filtered(lambda c: c.estado == 'Cancelado')
            record.afp_rechazados = record.riesgo_afp_ids.filtered(lambda c: c.estado == 'Rechazado')

    afp_comunicados = fields.One2many('riesgo.afp', 'riesgo_id', compute='_compute_afp')
    afp_pendientes = fields.One2many('riesgo.afp', 'riesgo_id', compute='_compute_afp')
    afp_cancelados = fields.One2many('riesgo.afp', 'riesgo_id', compute='_compute_afp')
    afp_rechazados = fields.One2many('riesgo.afp', 'riesgo_id', compute='_compute_afp')

# ---------
# Prórrogas
# ---------

    @api.depends('riesgo_prorroga_ids.estado')
    def _compute_prorroga(self):
        for record in self:
            record.prorrogas_comunicadas = record.riesgo_prorroga_ids.filtered(lambda c: c.estado == 'Comunicada')
            record.prorrogas_canceladas = record.riesgo_prorroga_ids.filtered(lambda c: c.estado == 'Cancelada')
            record.prorrogas_pendientes = record.riesgo_prorroga_ids.filtered(lambda c: c.estado == 'Pendiente')
            record.prorrogas_rechazadas = record.riesgo_prorroga_ids.filtered(lambda c: c.estado == 'Rechazada')

    prorrogas_comunicadas = fields.One2many('riesgo.prorroga', 'riesgo_id', compute='_compute_prorroga')
    prorrogas_pendientes = fields.One2many('riesgo.prorroga', 'riesgo_id', compute='_compute_prorroga')
    prorrogas_canceladas = fields.One2many('riesgo.prorroga', 'riesgo_id', compute='_compute_prorroga')
    prorrogas_rechazadas = fields.One2many('riesgo.prorroga', 'riesgo_id', compute='_compute_prorroga')

# ----------
# Siniestros
# ----------

    @api.depends('riesgo_siniestro_ids.estado')
    def _compute_siniestro(self):
        for record in self:
            record.siniestros_abiertos = record.riesgo_siniestro_ids.filtered(lambda c: c.estado == 'Abierto')
            record.siniestros_pendientes = record.riesgo_siniestro_ids.filtered(lambda c: c.estado == 'Pendiente')
            record.siniestros_anulados = record.riesgo_siniestro_ids.filtered(lambda c: c.estado == 'Anulado')
            record.siniestros_terminados = record.riesgo_siniestro_ids.filtered(lambda c: c.estado == 'Terminado')

    siniestros_abiertos = fields.One2many('riesgo.siniestro', 'riesgo_id', compute='_compute_siniestro')
    siniestros_pendientes = fields.One2many('riesgo.siniestro', 'riesgo_id', compute='_compute_siniestro')
    siniestros_anulados = fields.One2many('riesgo.siniestro', 'riesgo_id', compute='_compute_siniestro')
    siniestros_terminados = fields.One2many('riesgo.siniestro', 'riesgo_id', compute='_compute_siniestro')

# -------
# Alertas
# -------

    @api.depends('riesgo_alerta_ids.estado')
    def _compute_alerta(self):
        for record in self:
            record.alertas_nuevas = record.riesgo_alerta_ids.filtered(lambda c: c.estado == 'Nueva')
            record.alertas_leidas = record.riesgo_alerta_ids.filtered(lambda c: c.estado == 'Leida')

    alertas_nuevas = fields.One2many('riesgo.alerta', 'riesgo_id', compute='_compute_alerta')
    alertas_leidas = fields.One2many('riesgo.alerta', 'riesgo_id', compute='_compute_alerta')

# -----------------------
# Request Actions to CyC
# -----------------------
    
    def _check_required_fields(self):
        if not self.vat or len(self.vat) > 20:
            raise UserError("Por favor, complete el NIF (máximo 20 caracteres).")
        if not self.name:
            raise UserError("Por favor, complete el nombre del cliente.")
        if not self.country_id or not self.country_id.name:
            raise UserError("Por favor, seleccione un país.")

    def action_create_afp(self):
        self._check_required_fields()

        # Construir el dominio dinámico incluyendo el partner_id
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('amount_residual', '>', 0),
            ('date_maturity', '<', fields.Date.today()),
            ('parent_state', '=', 'posted')
        ]

        # Devuelve la acción con el dominio dinámico
        action = self.env.ref('credito-caucion.action_vencimientos_impagados').read()[0]
        action['domain'] = domain

        # Agregar action_type al contexto
        action['context'] = dict(self.env.context,  default_partner_id=self.partner_id.id, action_type='afp')
        
        return action
        
    def action_create_prorroga(self):
        self._check_required_fields()

        # Construir el dominio dinámico incluyendo el partner_id
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('amount_residual', '>', 0),
            ('date_maturity', '<', fields.Date.today()),
            ('parent_state', '=', 'posted')
        ]

        # Devuelve la acción con el dominio dinámico
        action = self.env.ref('credito-caucion.action_vencimientos_impagados').read()[0]
        action['domain'] = domain

        # Agregar action_type al contexto
        action['context'] = dict(self.env.context,  default_partner_id=self.partner_id.id, action_type='prorroga')
        
        return action

    def action_create_siniestro(self):
        self._check_required_fields()

        # Construir el dominio dinámico incluyendo el partner_id
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('amount_residual', '>', 0),
            ('date_maturity', '<', fields.Date.today()),
            ('parent_state', '=', 'posted')
        ]

        # Devuelve la acción con el dominio dinámico
        action = self.env.ref('credito-caucion.action_vencimientos_impagados').read()[0]
        action['domain'] = domain

        # Agregar action_type al contexto
        action['context'] = dict(self.env.context,  default_partner_id=self.partner_id.id, action_type='siniestro')
        
        return action

# -------------------------------------------------
# Delete/Cancel Actions (agregar llamadas a la api)
# -------------------------------------------------

    def action_delete_classification_en_vigor(self):
        if self.clasificacion_en_vigor:
            for clasificacion in self.clasificacion_en_vigor:
                clasificacion.estado = 'Pendiente'
                clasificacion.status = 'Pendiente de Desclasificar'
        else:
            raise UserError("No hay ninguna clasificación en vigor para eliminar.")
        return

    def action_cancel_all_afp(self):
        if self.afp_comunicados:
            for afp in self.afp_comunicados:
                afp.estado = 'Pendiente'
                afp.status = 'Pendiente de Cancelar'
        else:
            raise UserError("No hay ningun AFP comunicado para cancelar.")
        return

    def action_cancel_all_prorrogas(self):
        if self.prorrogas_comunicadas:
            for prorroga in self.prorrogas_comunicadas:
                prorroga.estado = 'Pendiente'
                prorroga.status = 'Pendiente de Cancelar'
        else:
            raise UserError("No hay ninguna Prórroga comunicada para cancelar.")
        return

# -----------------
# Dashboard General
# -----------------

    @api.model
    def get_kpi_data(self):
        _logger.info("Obteniendo datos KPI con importes...")

        # Clasificaciones
        clasificaciones_count = self.env['riesgo.clasificacion'].search_count([('estado', '=', 'En Vigor')])
        clasificaciones_importe = sum(self.env['riesgo.clasificacion'].search([('estado', '=', 'En Vigor')]).mapped('importe_concedido'))

        _logger.info("Clasificaciones en vigor: %s, Importe total: %s", clasificaciones_count, clasificaciones_importe)

        # AFP
        afp_count = self.env['riesgo.afp'].search_count([('estado', '=', 'Comunicado')])
        afp_importe = sum(self.env['riesgo.afp'].search([('estado', '=', 'Comunicado')]).mapped('importe_impagado'))

        _logger.info("AFPs en vigor: %s, Importe total: %s", afp_count, afp_importe)

        # Prórrogas
        prorrogas_count = self.env['riesgo.prorroga'].search_count([('estado', '=', 'Comunicada')])
        prorrogas_importe = sum(self.env['riesgo.prorroga'].search([('estado', '=', 'Comunicada')]).mapped('importe_prorrogado'))

        _logger.info("Prórrogas en vigor: %s, Importe total: %s", prorrogas_count, prorrogas_importe)

        # Siniestros
        siniestros_count = self.env['riesgo.siniestro'].search_count([('estado', 'in', ['Pendiente', 'Abierto'])])
        siniestros_importe = sum(self.env['riesgo.siniestro'].search([('estado', 'in', ['Pendiente', 'Abierto'])]).mapped('credito_total'))

        _logger.info("Siniestros en vigor: %s, Importe total: %s", siniestros_count, siniestros_importe)

        kpi_data = {
            'clasificaciones': clasificaciones_count,
            'clasificaciones_importe': clasificaciones_importe,
            'afp': afp_count,
            'afp_importe': afp_importe,
            'prorrogas': prorrogas_count,
            'prorrogas_importe': prorrogas_importe,
            'siniestros': siniestros_count,
            'siniestros_importe': siniestros_importe,
        }
        
        return kpi_data

    @api.model
    def get_clasificacion_distribucion(self):
        intervals = [
            (0, 6000),
            (6000, 12000),
            (12000, 20000),
            (20000, 30000),
            (30000, 50000),
            (50000, 100000),
            (100000, 250000),
            (250000, 500000),
            (500000, 1000000),
            (1000000, 99999999999),
        ]
        
        # Obtener el total global de `importe_concedido`
        total_global_sum = sum(self.env['riesgo.clasificacion'].search([('estado', '=', 'En Vigor')]).mapped('importe_concedido'))
        
        distribucion_data = []

        # Revisar cada intervalo
        for interval in intervals:
            records_in_interval = self.env['riesgo.clasificacion'].search([
                ('estado', '=', 'En Vigor'),
                ('importe_concedido', '>=', interval[0]),
                ('importe_concedido', '<', interval[1]),
            ])

            # Calcular el importe total para el intervalo
            interval_sum = sum(records_in_interval.mapped('importe_concedido'))
            
            # Calcular el porcentaje
            porcentaje = round((interval_sum / total_global_sum * 100), 2) if total_global_sum > 0 else 0
            
            distribucion_data.append({
                'total_importe': interval_sum,
                'porcentaje': porcentaje,
            })

        return distribucion_data

    @api.model
    def get_incidencias_cobro(self):
        # Obtener la fecha actual
        today = datetime.today()

        # Calcular los últimos 12 meses de manera dinámica, empezando por el mes actual
        meses = [(today - timedelta(days=30 * i)).strftime('%b') for i in range(11, -1, -1)]

        # Inicializamos los resultados para las 3 categorías (avisos de falta de pago, prórrogas, siniestros)
        resultados = {
            'avisos_falta_pago': [0] * 12,
            'prorrogas': [0] * 12,
            'siniestros': [0] * 12,
        }

        # Consultamos los registros necesarios
        afps = self.env['riesgo.afp'].search([])
        prorrogas = self.env['riesgo.prorroga'].search([])
        siniestros = self.env['riesgo.siniestro'].search([])

        # Procesamos los AFPs
        for afp in afps:
            if afp.fecha_vencimiento:
                # Convertimos la fecha de vencimiento a un objeto datetime
                fecha_vencimiento_date = fields.Date.from_string(afp.fecha_vencimiento)

                # Calculamos la diferencia en meses desde el mes actual
                diferencia_meses = (today.year - fecha_vencimiento_date.year) * 12 + (today.month - fecha_vencimiento_date.month)

                # Si está dentro de los últimos 12 meses, actualizamos el resultado
                if 0 <= diferencia_meses < 12:
                    resultados['avisos_falta_pago'][11 - diferencia_meses] += afp.importe_impagado

        # Procesamos las prórrogas
        for prorroga in prorrogas:
            if prorroga.fecha_vencimiento:
                fecha_vencimiento_date = fields.Date.from_string(prorroga.fecha_vencimiento)
                diferencia_meses = (today.year - fecha_vencimiento_date.year) * 12 + (today.month - fecha_vencimiento_date.month)
                if 0 <= diferencia_meses < 12:
                    resultados['prorrogas'][11 - diferencia_meses] += prorroga.importe_prorrogado

        # Procesamos los siniestros
        for siniestro in siniestros:
            if siniestro.fecha_declaracion:
                fecha_declaracion_date = fields.Date.from_string(siniestro.fecha_declaracion)
                diferencia_meses = (today.year - fecha_declaracion_date.year) * 12 + (today.month - fecha_declaracion_date.month)
                if 0 <= diferencia_meses < 12:
                    resultados['siniestros'][11 - diferencia_meses] += siniestro.credito_total

        # Retornamos los meses y los datasets con los resultados calculados
        return {
            'labels': meses,
            'datasets': resultados
        }

    @api.model
    def calcular_riesgo_clientes(self):
        # Inicializamos los resultados para las 5 categorías de riesgo
        riesgo_categorias = {
            'maximo': 0,
            'alto': 0,
            'moderado': 0,
            'bajo': 0,
            'minimo': 0,
        }
        
        # Buscamos todas las clasificaciones activas
        clasificaciones = self.env['riesgo.clasificacion'].search([('estado', '=' , 'En Vigor')]) 
        
        for clasificacion in clasificaciones:
            if clasificacion.importe_solicitado > 0:
                # Calculamos el riesgo base: importe concedido / importe solicitado
                proporcion_riesgo = clasificacion.importe_concedido / clasificacion.importe_solicitado
                
                # Aplicamos las penalizaciones por AFP, prórrogas o siniestros
                afps = self.env['riesgo.afp'].search([('riesgo_id', '=', clasificacion.riesgo_id.id)])
                prorrogas = self.env['riesgo.prorroga'].search([('riesgo_id', '=', clasificacion.riesgo_id.id)])
                siniestros = self.env['riesgo.siniestro'].search([('riesgo_id', '=', clasificacion.riesgo_id.id)])

                # Por cada AFP o prórroga, se resta un 5%
                for afp in afps:
                    proporcion_riesgo = proporcion_riesgo/2
                for prorroga in prorrogas:
                    proporcion_riesgo = proporcion_riesgo/2

                # Si tiene siniestros, se resta un 50% adicional
                if siniestros:
                    proporcion_riesgo = 0

                # Convertimos a porcentaje
                proporcion_riesgo = proporcion_riesgo*100

                # Clasificamos en las 5 categorías de riesgo
                if proporcion_riesgo <= 20:
                    riesgo_categorias['maximo'] += 1
                elif 20 < proporcion_riesgo <= 40:
                    riesgo_categorias['alto'] += 1
                elif 40 < proporcion_riesgo <= 60:
                    riesgo_categorias['moderado'] += 1
                elif 60 < proporcion_riesgo <= 80:
                    riesgo_categorias['bajo'] += 1
                else:
                    riesgo_categorias['minimo'] += 1
        
        # Retornamos los resultados que luego serán usados para la gráfica
        return riesgo_categorias

# ------------------
# Dashboard Facturas
# ------------------

    @api.model
    def get_kpi_facturas_data(self):
        # KPI 1: Gestor de Clasificaciones 
        gestor_clasificaciones = self.env['riesgo'].search_count([
            ('estado_clasificacion', 'in', ['clasificar', 'ampliar', 'reducir', 'eliminar'])
        ])
        
        # KPI 2: Gestor de Cobros
        gestor_cobros = self.env['account.move.line'].search_count([
            ('tiene_boton_activo', '=', True),
            ('parent_state', '=', 'posted'),
            ('display_type', '=', 'payment_term'),
            ('debit', '>', 0)
        ])

        # Retornar los valores en formato de diccionario
        kpi_facturas_data =  {
            'gestor_clasificaciones': gestor_clasificaciones,
            'gestor_cobros': gestor_cobros,
        }

        return kpi_facturas_data
   
# ----------
# Saldo Vivo
# ----------

    vencimientos_pendientes_ids = fields.One2many('account.move.line', string="Vencimientos Pendientes", compute='_compute_vencimientos_pendientes')
    pedidos_abiertos_ids = fields.One2many('sale.order', string="Pedidos Abiertos", compute='_compute_pedidos_abiertos')
    
    saldo_vivo = fields.Float(string="Saldo Vivo", compute='_compute_saldo_vivo')
    duracion_ventas = fields.Selection([
        ('30', '30 días'),
        ('60', '60 días'),
        ('90', '90 días'),
        ('120', '120 días'),
        ('150', '150 días'),
        ('180', '180 días'),
    ], string='Duración de Ventas')

    @api.depends('partner_id')
    def _compute_saldo_vivo(self):
        """
        Computa el saldo vivo sumando el importe residual de los vencimientos pendientes y los pedidos abiertos.
        """
        for record in self:
            saldo_vivo_vencimientos = sum(record.vencimientos_pendientes_ids.mapped('amount_residual'))
            saldo_vivo_pedidos = sum(record.pedidos_abiertos_ids.mapped('amount_total'))
            record.saldo_vivo = saldo_vivo_vencimientos + saldo_vivo_pedidos

    @api.depends('partner_id')
    def _compute_vencimientos_pendientes(self):
        """
        Obtiene los vencimientos pendientes para el cliente asociado.
        """
        for record in self:
            record.vencimientos_pendientes_ids = self.env['account.move.line'].search([
                ('partner_id', '=', record.partner_id.id),
                ('display_type', '=', 'payment_term'),
                ('amount_residual', '>', 0),
                ('parent_state', '=', 'posted')  # Solo se consideran vencimientos de facturas publicadas
            ])

    @api.depends('partner_id')
    def _compute_pedidos_abiertos(self):
        """
        Obtiene los pedidos abiertos que aún no están completamente facturados para el cliente asociado.
        """
        for record in self:
            record.pedidos_abiertos_ids = self.env['sale.order'].search([
                ('partner_id', '=', record.partner_id.id),
                ('state', 'in', ['sale', 'done']),
                ('invoice_status', '!=', 'invoiced')
            ])

# -------------------------
# Gestor de Clasificaciones
# -------------------------

    facturado_ultimo_periodo = fields.Float(string="Facturado Último Periodo", compute="_compute_facturado_ultimo_periodo")
    tiempo_desde_ultimo_pedido = fields.Integer(string="Días Desde Último Pedido", store=True, compute="_compute_tiempo_desde_ultimo_pedido")
    
    estado_clasificacion = fields.Selection([
        ('clasificar', 'Clasificar'),
        ('ampliar', 'Ampliar'),
        ('reducir', 'Reducir'),
        ('eliminar', 'Eliminar'),
        ('correcto', 'Correcto'),
        ('pendiente', 'Pendiente'),
    ], string="Estado Clasificación", compute="_compute_estado_clasificacion", store=True, index=True, default='correcto')

    @api.depends('saldo_vivo', 'importe_concedido', 'duracion_ventas')
    def _compute_estado_clasificacion(self):
        for record in self:
            if record.estado_clasificacion != 'pendiente':
                if not record.importe_concedido and record.saldo_vivo > 0:
                    record.estado_clasificacion = 'clasificar'
                elif record.saldo_vivo > record.importe_concedido:
                    record.estado_clasificacion = 'ampliar'
                elif record.tiempo_desde_ultimo_pedido:
                    if record.tiempo_desde_ultimo_pedido > 365 :
                        record.estado_clasificacion = 'eliminar'
                elif record.saldo_vivo + record.facturado_ultimo_periodo < record.importe_concedido * 0.5:
                    record.estado_clasificacion = 'reducir'

    @api.depends('saldo_vivo', 'duracion_ventas')
    def _compute_facturado_ultimo_periodo(self):
        for record in self:
            try:
                # Asegúrate de que `duracion_ventas` sea un número entero
                duracion_ventas_dias = int(record.duracion_ventas) if record.duracion_ventas else 0
                
                # Calcular la fecha de inicio en base a la duración de ventas
                fecha_inicio = fields.Date.today() - timedelta(days=duracion_ventas_dias)
                
                # Obtener facturas pagadas desde la fecha de inicio
                facturas_pagadas = self.env['account.move'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('move_type', '=', 'out_invoice'),
                    ('payment_state', '=', 'paid'),
                    ('invoice_date', '>=', fecha_inicio)
                ])
   
                record.facturado_ultimo_periodo = sum(factura.amount_total for factura in facturas_pagadas)

            except ValueError:
                record.facturado_ultimo_periodo = 0.0

    @api.depends('saldo_vivo', 'duracion_ventas')
    def _compute_tiempo_desde_ultimo_pedido(self):
        for record in self:
            ultimo_pedido = self.env['sale.order'].search([
                ('partner_id', '=', record.partner_id.id),
                ('state', 'in', ['sale', 'done'])
            ], order='date_order desc', limit=1)
            
            if ultimo_pedido:
                fecha_ultimo_pedido = ultimo_pedido.date_order.date()
                fecha_actual = fields.Date.today()
                dias_desde_ultimo_pedido = (fecha_actual - fecha_ultimo_pedido).days
                record.tiempo_desde_ultimo_pedido = dias_desde_ultimo_pedido
            else:
                record.tiempo_desde_ultimo_pedido = -1
    
    def action_abrir_wizard_clasificacion(self):
        self._check_required_fields()
        # Obtener el tipo de acción desde el contexto
        action_type = self.env.context.get('action_type')
        importe_sugerido = round(self.saldo_vivo / 1000.0 + 1) * 1000

        if action_type == 'eliminar':
            importe_sugerido = 0

        return {
            'name': 'Solicitar ' + action_type.capitalize(),
            'type': 'ir.actions.act_window',
            'res_model': 'create.riesgo.clasificacion',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_importe_solicitado': importe_sugerido,
                'default_importe_concedido': self.importe_concedido,
                'default_riesgo_id': self.id,
                'default_action_type': action_type,  # Pasar el tipo de acción
            }
        }

