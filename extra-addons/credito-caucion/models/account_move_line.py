from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

import requests
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

# ----------------
# GESTOR DE COBROS
# ----------------

    # Campos calculados para el límite de comunicación
    limite_comunicar_afp = fields.Date(string="Límite Comunicar AFP", compute='_compute_limite_comunicacion', store=True)
    limite_comunicar_prorroga = fields.Date(string="Límite Comunicar Prórroga", compute='_compute_limite_comunicacion', store=True)
    limite_comunicar_siniestro = fields.Date(string="Límite Comunicar Siniestro", compute='_compute_limite_comunicacion', store=True)

    # Método de cálculo de las fechas límite usando los settings
    @api.depends('date_maturity')
    def _compute_limite_comunicacion(self):
        # Obtener valores de configuración desde res.config.settings
        param_env = self.env['ir.config_parameter'].sudo()
        dias_afp = int(param_env.get_param('credito_caucion.comunicacion_afp', default=60))
        dias_prorroga = int(param_env.get_param('credito_caucion.duracion_maxima_credito', default=90))
        dias_siniestro = int(param_env.get_param('credito_caucion.declaracion_siniestro', default=120))

        for record in self:
            if record.date_maturity:
                # Usar los valores configurados en los settings
                record.limite_comunicar_afp = record.date_maturity + timedelta(days=dias_afp)
                record.limite_comunicar_prorroga = record.date_maturity + timedelta(days=dias_prorroga)
                record.limite_comunicar_siniestro = record.date_maturity + timedelta(days=dias_siniestro)
            else:
                # Si no hay fecha de vencimiento, los valores deben ser nulos
                record.limite_comunicar_afp = False
                record.limite_comunicar_prorroga = False
                record.limite_comunicar_siniestro = False

    estado_riesgo = fields.Selection([
        ('en plazo', 'En Plazo'),
        ('impagado', 'Impagado'),
        ('cobrado', 'Cobrado')
    ], string="Estado Riesgo", store=True)

    estado_recordatorio_pago = fields.Selection([
        ('no enviado', 'No Enviado'),
        ('recordatorio de pago enviado', 'Recordatorio de Pago Enviado'),
        ('recordatorio de pago prorroga 1 enviado', 'Recordatorio de Pago Prórroga 1 Enviado'),
        ('recordatorio de pago prorroga 2 enviado', 'Recordatorio de Pago Prórroga 2 Enviado'),
        ('recordatorio de pago prorroga especial enviado', 'Recordatorio de Pago Prórroga Especial Enviado'),
    ], string="Estado Recordatorio de Pago", default="no enviado", store=True)

    estado_afp = fields.Selection([
        ('no comunicado', 'No Comunicado'),
        ('afp comunicado', 'AFP Comunicado'),
        ('afp prorroga 1 comunicado', 'AFP Prórroga 1 Comunicado'),
        ('afp prorroga 2 comunicado', 'AFP Prórroga 2 Comunicado'),
    ], string="Estado AFP", default="no comunicado", store=True)

    estado_prorroga = fields.Selection([
        ('no comunicada', 'No Comunicada'),
        ('prorroga comunicada', 'Prórroga Comunicada'),
        ('segunda prorroga comunicada', 'Segunda Prórroga Comunicada'),
        ('prorroga especial comunicada', 'Prórroga Especial Comunicada'),
    ], string="Estado Prórroga", default="no comunicada", store=True)

    estado_siniestro = fields.Selection([
        ('no declarado', 'No Declarado'),
        ('siniestro declarado', 'Siniestro Declarado'),
    ], string="Estado AFP", default="no declarado", store=True)
    
# --------------------------------------
# COMPUTE BOOLEANOS PARA MOSTRAR BOTONES
# --------------------------------------

    mostrar_boton_recordatorio = fields.Boolean(compute="_compute_flujo_cobro", default=False)
    mostrar_boton_afp = fields.Boolean(compute="_compute_flujo_cobro", default=False)
    mostrar_boton_prorroga = fields.Boolean(compute="_compute_flujo_cobro", default=False)
    mostrar_boton_siniestro = fields.Boolean(compute="_compute_flujo_cobro", default=False)
    mostrar_boton_cancelar_incidencias = fields.Boolean(compute="_compute_flujo_cobro", default=False)

    @api.depends('estado_afp', 'estado_prorroga', 'estado_siniestro', 'estado_recordatorio_pago', 'date_maturity', 'amount_residual')
    def _compute_flujo_cobro(self):
        hoy = fields.Date.context_today(self)
        param_env = self.env['ir.config_parameter'].sudo()
        
        # Obtener valores configurados para cada fase
        dias_aviso_recordatorio = int(param_env.get_param('credito_caucion.dias_recordatorio_pago_aviso'))
        dias_prorroga_aviso = int(param_env.get_param('credito_caucion.dias_prorroga_aviso'))
        dias_afp_aviso = int(param_env.get_param('credito_caucion.dias_afp_aviso'))
        dias_siniestro_aviso = int(param_env.get_param('credito_caucion.dias_siniestro_aviso'))

        for record in self:
            record.mostrar_boton_recordatorio = False
            record.mostrar_boton_afp = False
            record.mostrar_boton_prorroga = False
            record.mostrar_boton_siniestro = False
            record.mostrar_boton_cancelar_incidencias = False

            tiene_incidencias_comunicadas = record.afp_ids.filtered(lambda a: a.estado == 'Comunicado') or \
                                            record.prorroga_ids.filtered(lambda p: p.estado == 'Comunicada') or \
                                            record.siniestro_ids.filtered(lambda s: s.estado == 'Comunicado')

            # Condición para cancelar incidencias si el saldo es cero y existen incidencias comunicadas
            if record.amount_residual == 0:
                if tiene_incidencias_comunicadas:
                    record.mostrar_boton_cancelar_incidencias = True
                continue

            # Fase: Siniestro declarado
            if record.estado_siniestro == 'siniestro declarado':
                continue

            if record.date_maturity:
                dias_diferencia = (record.date_maturity - hoy).days

                # Fase de Prórroga: No comunicada
                if record.estado_prorroga == 'no comunicada':
                    if hoy <= record.date_maturity and dias_diferencia <= dias_prorroga_aviso:
                        record.mostrar_boton_prorroga = True
                        if record.estado_recordatorio_pago != 'recordatorio de pago enviado' and dias_diferencia <= dias_aviso_recordatorio:
                            record.mostrar_boton_recordatorio = True
                    elif hoy > record.date_maturity and dias_diferencia < -dias_afp_aviso:
                        if record.estado_afp != 'afp comunicado':
                            record.mostrar_boton_afp = True
                        else:
                            record.mostrar_boton_prorroga = True
                            record.mostrar_boton_siniestro = True

                # Fase de Prórroga: Primera prórroga comunicada
                elif record.estado_prorroga == 'prorroga comunicada':
                    if hoy <= record.date_maturity and dias_diferencia <= dias_prorroga_aviso:
                        record.mostrar_boton_prorroga = True
                        if record.estado_recordatorio_pago != 'recordatorio de pago prorroga 1 enviado' and dias_diferencia <= dias_aviso_recordatorio:
                            record.mostrar_boton_recordatorio = True
                    elif hoy > record.date_maturity and dias_diferencia < -dias_afp_aviso:
                        if record.estado_afp != 'afp prorroga 1 comunicado':
                            record.mostrar_boton_afp = True
                        else:
                            record.mostrar_boton_prorroga = True
                            record.mostrar_boton_siniestro = True

                # Fase de Prórroga: Segunda prórroga comunicada
                elif record.estado_prorroga == 'segunda prorroga comunicada':
                    if hoy <= record.date_maturity and dias_diferencia <= dias_prorroga_aviso:
                        record.mostrar_boton_prorroga = True
                        if record.estado_recordatorio_pago != 'recordatorio de pago prorroga 2 enviado' and dias_diferencia <= dias_aviso_recordatorio:
                            record.mostrar_boton_recordatorio = True
                    elif hoy > record.date_maturity and dias_diferencia < -dias_afp_aviso:
                        if record.estado_afp != 'afp prorroga 2 comunicado':
                            record.mostrar_boton_afp = True
                        else:
                            record.mostrar_boton_prorroga = True
                            record.mostrar_boton_siniestro = True

                # Fase de Prórroga: Prórroga especial comunicada
                elif record.estado_prorroga == 'prorroga especial comunicada':
                    if record.estado_recordatorio_pago != 'recordatorio de pago prorroga especial enviado' and dias_diferencia <= dias_aviso_recordatorio:
                        record.mostrar_boton_recordatorio = True
                    elif hoy > record.date_maturity and dias_diferencia < -dias_siniestro_aviso:
                        record.mostrar_boton_siniestro = True

    tiene_boton_activo = fields.Boolean(
        string="Tiene Botón Activo",
        compute="_compute_tiene_boton_activo",
        store=True
    )

    @api.depends('mostrar_boton_recordatorio', 'mostrar_boton_afp', 'mostrar_boton_prorroga', 'mostrar_boton_siniestro', 'mostrar_boton_cancelar_incidencias')
    def _compute_tiene_boton_activo(self):
        for record in self:
            record.tiene_boton_activo = any([
                record.mostrar_boton_recordatorio,
                record.mostrar_boton_afp,
                record.mostrar_boton_prorroga,
                record.mostrar_boton_siniestro,
                record.mostrar_boton_cancelar_incidencias
            ])

# ---------------------
# COMUNICAR INCIDENCIAS
# ---------------------

    def action_enviar_recordatorio_pago(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'recordatorio.pago.wizard',
            'name': 'Recordatorio de Pago',
            'view_mode': 'form',
            'view_id': self.env.ref('credito-caucion.view_recordatorio_pago_wizard_form').id,
            'target': 'new',
            'context': {
                'default_vencimiento_id': self.id,
                'default_partner_id': self.partner_id.id, 
            }
        }
    
    def action_comunicar_afp(self):
        """
        Abre el wizard para comunicar AFP de la factura seleccionada.
        """
        # Verificamos si el cliente tiene un perfil de riesgo asociado
        if not self.partner_id.riesgo_id:
            raise UserError("El cliente no tiene un perfil de riesgo asociado.")

        # Verificamos si el riesgo_id es un entero válido
        riesgo_id = self.partner_id.riesgo_id.id
        if not isinstance(riesgo_id, int):
            raise UserError("El perfil de riesgo no es válido.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comunicar AFP',
            'view_mode': 'form',
            'res_model': 'create.riesgo.afp',
            'view_id': self.env.ref('credito-caucion.view_form_create_riesgo_afp').id,
            'target': 'new',
            'context': {
                'default_vencimiento_ids': self.ids,  # Many2many necesita una lista de IDs
                'default_riesgo_id': riesgo_id, 
                'default_importe_impagado': self.amount_residual, 
                'default_fecha_vencimiento': self.date_maturity,  
            }
        }

    def action_comunicar_prorroga(self):
        """
        Abre el wizard para comunicar Prórroga de la factura seleccionada.
        """
        # Verificamos si el cliente tiene un perfil de riesgo asociado
        if not self.partner_id.riesgo_id:
            raise UserError("El cliente no tiene un perfil de riesgo asociado.")

        # Verificamos si el riesgo_id es un entero válido
        riesgo_id = self.partner_id.riesgo_id.id
        if not isinstance(riesgo_id, int):
            raise UserError("El perfil de riesgo no es válido.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comunicar Prórroga',
            'view_mode': 'form',
            'res_model': 'create.riesgo.prorroga',
            'view_id': self.env.ref('credito-caucion.view_form_create_riesgo_prorroga').id,
            'target': 'new',
            'context': {
                'default_vencimiento_ids': self.ids,  # Many2many necesita una lista de IDs
                'default_riesgo_id': riesgo_id, 
                'default_importe_prorrogado': self.amount_residual, 
                'default_fecha_vencimiento': self.date_maturity,  
            }
        }

    def action_declarar_siniestro(self):
        """
        Abre el wizard para comunicar un siniestro, incluyendo todos los cobros pendientes de este cliente.
        """
        # Verificar si el cliente tiene un perfil de riesgo asociado
        if not self.partner_id.riesgo_id:
            raise UserError("El cliente no tiene un perfil de riesgo asociado.")

        # Obtener el ID del perfil de riesgo
        riesgo_id = self.partner_id.riesgo_id.id
        if not isinstance(riesgo_id, int):
            raise UserError("El perfil de riesgo no es válido.")
        
        # Obtener todos los cobros pendientes para este cliente
        vencimientos_pendientes = self.env['account.move.line'].search([
            ('partner_id', '=', self.partner_id.id),
            ('amount_residual', '>', 0)  # Solo cobros pendientes
        ])

        # Sumar el saldo vivo total para todos los cobros pendientes
        credito_total = sum(vencimientos_pendientes.mapped('amount_residual'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Declarar Siniestro',
            'view_mode': 'form',
            'res_model': 'create.riesgo.siniestro',
            'view_id': self.env.ref('credito-caucion.view_form_create_riesgo_siniestro').id,
            'target': 'new',
            'context': {
                'default_vencimiento_ids': vencimientos_pendientes.ids,  # Lista de IDs de cobros pendientes
                'default_riesgo_id': riesgo_id, 
                'default_credito_total': credito_total,  # Monto total de todos los cobros pendientes
                'default_fecha_impago': self.date_maturity,  
            }
        }

    def action_cancelar_incidencias(self):
        return

# ----------------------
# RELACIONES INCIDENCIAS
# ----------------------    

    afp_ids = fields.Many2many('riesgo.afp', string='AFP', ondelete="cascade")
    prorroga_ids = fields.Many2many('riesgo.prorroga', string='Prórrogas', ondelete="cascade")
    siniestro_ids = fields.Many2many('riesgo.siniestro', string='Siniestros', ondelete="cascade")

# -------------------------------
# RECORDATORIO DE PAGO A DEUDORES
# -------------------------------
    
    recordatorio_enviado = fields.Boolean(string="Recordatorio Enviado", default=False)
    fecha_recordatorio = fields.Datetime(string="Fecha de Recordatorio")

    def action_enviar_recordatorio(self):
        self.ensure_one()
        if self.recordatorio_enviado:
            raise UserError("El recordatorio de pago ya ha sido enviado al cliente.")

        return {
            'name': 'Enviar Recordatorio de Pago',
            'type': 'ir.actions.act_window',
            'res_model': 'recordatorio.pago.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id}
        }
    
# --------------------------------------
# CANCELAR INCIDENCIAS AL REGISTRAR PAGO
# --------------------------------------

    def _cancel_afp_prorroga_siniestro(self):
        """
        Cancela AFP, Prórroga o Siniestro si están en estado 'Comunicado'
        y el saldo restante de la factura es 0 (pago completo).
        """
        for move in self:
            if move.amount_residual == 0:  # Si el pago es completo
                afp = self.env['riesgo.afp'].search([('invoice_id', '=', move.id), ('estado', '=', 'Comunicado')], limit=1)
                prorroga = self.env['riesgo.prorroga'].search([('invoice_id', '=', move.id), ('estado', '=', 'Comunicada')], limit=1)
                siniestro = self.env['riesgo.siniestro'].search([('invoice_id', '=', move.id), ('estado', '=', 'Comunicado')], limit=1)

        if afp:
            afp.action_cancel_afp()  # Llamamos al método de cancelar AFP
        if prorroga:
            prorroga.action_cancel_prorroga()  # Llamamos al método de cancelar prórroga
        if siniestro:
            return
            siniestro.action_cancel_siniestro()  # Llamamos al método de cancelar siniestro

# ---------------
# VER INCIDENCIAS 
# ---------------

    def action_view_afp(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'AFP',
            'res_model': 'riesgo.afp',
            'target': 'current',
        }
        
        if len(self.afp_ids) == 1:
            # Si hay solo un AFP, abre la vista de formulario
            action.update({
                'view_mode': 'form',
                'res_id': self.afp_ids.id,
            })
        else:
            # Si hay múltiples AFPs, abre la vista de lista
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.afp_ids.ids)],
            })
        
        return action

    def action_view_prorroga(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Prórroga',
            'res_model': 'riesgo.prorroga',
            'target': 'current',
        }
        
        if len(self.prorroga_ids) == 1:
            # Si hay solo una prórroga, abre la vista de formulario
            action.update({
                'view_mode': 'form',
                'res_id': self.prorroga_ids.id,
            })
        else:
            # Si hay múltiples prórrogas, abre la vista de lista
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.prorroga_ids.ids)],
            })
        
        return action

    def action_view_siniestro(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Siniestro',
            'res_model': 'riesgo.siniestro',
            'target': 'current',
        }
        
        if len(self.siniestro_ids) == 1:
            # Si hay solo un siniestro, abre la vista de formulario
            action.update({
                'view_mode': 'form',
                'res_id': self.siniestro_ids.id,
            })
        # (en principio esto nunca debe suceder, ya que no pueden haber más de un siniestro por cobro, pero lo hacemos así para que no de error en odoo)
        else:
            # Si hay múltiples siniestros, abre la vista de lista
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.siniestro_ids.ids)],
            })
        
        return action
    
# -----------------------------
# MÉTODOS COUNT (SMART BUTTONS)
# -----------------------------

    afp_count = fields.Integer(string="AFP Count", compute='_compute_afp_count')
    prorroga_count = fields.Integer(string="Prórroga Count", compute='_compute_prorroga_count')
    siniestro_count = fields.Integer(string="Siniestro Count", compute='_compute_siniestro_count')

    def _compute_afp_count(self):
        for line in self:
            line.afp_count = self.env['riesgo.afp'].search_count([('vencimiento_ids', '=', line.id)])

    def _compute_prorroga_count(self):
        for line in self:
            line.prorroga_count = self.env['riesgo.prorroga'].search_count([('vencimiento_ids', '=', line.id)])

    def _compute_siniestro_count(self):
        for line in self:
            line.siniestro_count = self.env['riesgo.siniestro'].search_count([('vencimiento_ids', '=', line.id)])

# ------------------
# DASHBOARD FACTURAS
# ------------------

    @api.model
    def get_saldo_vencimientos(self):
        intervalos = {
            'en_plazo': 0,
            '+1_15_dias': 0,
            '+15_30_dias': 0,
            '+31_60_dias': 0,
            '+61_90_dias': 0,
            '+91_dias': 0
        }

        hoy = fields.Date.context_today(self)

        # Buscar vencimientos no pagados
        vencimientos_no_pagados = self.search([
            ('display_type', '=', 'payment_term'),
            ('amount_residual', '>', 0),
            ('move_id.state', '=', 'posted')
        ])

        for vencimiento in vencimientos_no_pagados:
            if vencimiento.date_maturity:
                dias_de_vencimiento = (hoy - vencimiento.date_maturity).days

                if dias_de_vencimiento <= 0:
                    intervalos['en_plazo'] += vencimiento.amount_residual
                elif 1 <= dias_de_vencimiento <= 15:
                    intervalos['+1_15_dias'] += vencimiento.amount_residual
                elif 16 <= dias_de_vencimiento <= 30:
                    intervalos['+15_30_dias'] += vencimiento.amount_residual
                elif 31 <= dias_de_vencimiento <= 60:
                    intervalos['+31_60_dias'] += vencimiento.amount_residual
                elif 61 <= dias_de_vencimiento <= 90:
                    intervalos['+61_90_dias'] += vencimiento.amount_residual
                else:
                    intervalos['+91_dias'] += vencimiento.amount_residual

        return {
            'labels': ['En plazo', '+1-15 días', '+15-30 días', '+31-60 días', '+61-90 días', '+91 días'],
            'datasets': [
                intervalos['en_plazo'],
                intervalos['+1_15_dias'],
                intervalos['+15_30_dias'],
                intervalos['+31_60_dias'],
                intervalos['+61_90_dias'],
                intervalos['+91_dias']
            ]
        }

    @api.model
    def get_proximos_vencimientos(self):
        intervalos = {
            'hoy': 0,
            '1_15_dias': 0,
            '16_30_dias': 0,
            '31_45_dias': 0,
            '46_60_dias': 0,
            '61_75_dias': 0,
            '76_90_dias': 0,
            '91_120_dias': 0,
            '121_150_dias': 0,
            '151_180_dias': 0,
            '+181_dias': 0
        }

        hoy = fields.Date.context_today(self)

        # Buscar vencimientos no pagados y con fecha futura o igual a hoy
        vencimientos_pendientes = self.search([
            ('display_type', '=', 'payment_term'),
            ('date_maturity', '>=', hoy),
            ('amount_residual', '>', 0),
            ('move_id.state', '=', 'posted')
        ])

        for vencimiento in vencimientos_pendientes:
            if vencimiento.date_maturity:
                dias_restantes = (vencimiento.date_maturity - hoy).days

                if dias_restantes == 0:
                    intervalos['hoy'] += vencimiento.amount_residual
                elif 1 <= dias_restantes <= 15:
                    intervalos['1_15_dias'] += vencimiento.amount_residual
                elif 16 <= dias_restantes <= 30:
                    intervalos['16_30_dias'] += vencimiento.amount_residual
                elif 31 <= dias_restantes <= 45:
                    intervalos['31_45_dias'] += vencimiento.amount_residual
                elif 46 <= dias_restantes <= 60:
                    intervalos['46_60_dias'] += vencimiento.amount_residual
                elif 61 <= dias_restantes <= 75:
                    intervalos['61_75_dias'] += vencimiento.amount_residual
                elif 76 <= dias_restantes <= 90:
                    intervalos['76_90_dias'] += vencimiento.amount_residual
                elif 91 <= dias_restantes <= 120:
                    intervalos['91_120_dias'] += vencimiento.amount_residual
                elif 121 <= dias_restantes <= 150:
                    intervalos['121_150_dias'] += vencimiento.amount_residual
                elif 151 <= dias_restantes <= 180:
                    intervalos['151_180_dias'] += vencimiento.amount_residual
                else:
                    intervalos['+181_dias'] += vencimiento.amount_residual

        return {
            'labels': ['Hoy', '1-15 días', '16-30 días', '31-45 días', '46-60 días', '61-75 días', '76-90 días', '91-120 días', '121-150 días', '151-180 días', '+181 días'],
            'datasets': [
                intervalos['hoy'],
                intervalos['1_15_dias'],
                intervalos['16_30_dias'],
                intervalos['31_45_dias'],
                intervalos['46_60_dias'],
                intervalos['61_75_dias'],
                intervalos['76_90_dias'],
                intervalos['91_120_dias'],
                intervalos['121_150_dias'],
                intervalos['151_180_dias'],
                intervalos['+181_dias']
            ]
        }

    @api.model
    def get_ventas_cobros_dinamicos(self):
        meses_labels = []
        facturacion_mensual = [0] * 12
        cobros_mensual = [0] * 12
        saldo_vencimientos_mensual = [0] * 12
        deuda_fuera_plazo_mensual = [0] * 12

        hoy = fields.Date.context_today(self)

        for i in range(12):
            mes_actual = hoy.replace(day=1) - relativedelta(months=i)
            meses_labels.append(mes_actual.strftime('%b'))

            # Vencimientos del mes actual
            vencimientos_mes = self.search([
                ('display_type', '=', 'payment_term'),
                ('debit', '>', 0),
                ('invoice_date', '>=', mes_actual),
                ('invoice_date', '<', mes_actual + relativedelta(months=1)),
                ('parent_state', '=', 'posted')
            ])

            # Calcular facturación de vencimientos
            facturacion_mensual[i] = sum(vencimientos_mes.mapped('debit'))

            # Calcular saldo de vencimientos (que no han vencido)
            saldo_vencimientos_mes = vencimientos_mes.filtered(lambda v: v.date_maturity >= hoy and v.amount_residual > 0)
            saldo_vencimientos_mensual[i] = sum(saldo_vencimientos_mes.mapped('amount_residual'))

            # Calcular deuda fuera de plazo (que ya ha vencido)
            deuda_fuera_plazo_mes = vencimientos_mes.filtered(lambda v: v.date_maturity < hoy and v.amount_residual > 0)
            deuda_fuera_plazo_mensual[i] = sum(deuda_fuera_plazo_mes.mapped('amount_residual'))

            pagos_mes = self.env['account.payment'].search([
                ('date', '>=', mes_actual),
                ('date', '<', mes_actual + relativedelta(months=1)),
                ('state', '=', 'posted'),
                ('payment_type', '=', 'inbound')
            ])
            cobros_mensual[i] = sum(pagos_mes.mapped('amount'))

        meses_labels.reverse()
        facturacion_mensual.reverse()
        cobros_mensual.reverse()
        saldo_vencimientos_mensual.reverse()
        deuda_fuera_plazo_mensual.reverse()

        return {
            'labels': meses_labels,
            'facturacion': facturacion_mensual,
            'cobros': cobros_mensual,
            'saldo_vencimientos': saldo_vencimientos_mensual,
            'deuda_fuera_plazo': deuda_fuera_plazo_mensual
        }

    @api.model
    def get_top_10_customers_impagadas(self):
        # Buscar vencimientos no pagados (no reconciliados) y publicados
        vencimientos_no_pagados = self.search([
            ('display_type', '=', 'payment_term'),
            ('date_maturity', '<', fields.Date.context_today(self)),
            ('amount_residual', '>', 0),
            ('move_id.state', '=', 'posted')
        ])

        # Agrupar por cliente y sumar el monto residual (deuda pendiente)
        clientes_vencimientos = {}
        for vencimiento in vencimientos_no_pagados:
            cliente = vencimiento.partner_id
            if cliente not in clientes_vencimientos:
                clientes_vencimientos[cliente] = 0
            clientes_vencimientos[cliente] += vencimiento.amount_residual

        # Ordenar los clientes por monto de deuda y tomar los 10 primeros
        top_10_clientes = sorted(clientes_vencimientos.items(), key=lambda x: x[1], reverse=True)[:10]

        # Preparar los datos para el gráfico
        labels = [cliente.name for cliente, deuda in top_10_clientes]
        datasets = [deuda for cliente, deuda in top_10_clientes]

        return {
            'labels': labels,
            'datasets': datasets
        }
