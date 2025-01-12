from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Configuraciones de Póliza
    tipo_poliza = fields.Selection([
        ('lider', 'Líder'),
        ('lider+', 'Líder +'), 
        ('bonus', 'Bonus'),
        ('start', 'Start'),
        ('agil', 'Ágil')], 
        string="Tipo de Póliza", default="lider")
    email_agente_asegurador = fields.Char(string="Correo del Agente")
    
    # Capital 
    capital_asegurado = fields.Integer(string="Capital Asegurado")
    cifra_anonimos = fields.Integer(string="Cifra Anónimos")
    capital_interior = fields.Integer(string="Capital Interior")
    capital_exterior = fields.Integer(string="Capital Exterior")

    # Duraciones 
    duracion_maxima_credito = fields.Selection([
        ('30', '30 días'), 
        ('60', '60 días'), 
        ('90', '90 días'), 
        ('120', '120 días'), 
        ('150', '150 días'), 
        ('180', '180 días'), 
        ('210', '210 días'),
        ('240', '240 días'),
        ('270', '270 días'),
        ('300', '300 días'),
        ('330', '330 días'),
        ('360', '360 días')],
        string="Duración Máxima de Crédito", default="90")
    declaracion_ventas = fields.Selection([
        ('mensuales', 'Mensuales'),
        ('trimestrales', 'Trimestrales'),
        ('anuales', 'Anuales')],
        string="Declaración de Ventas", default="mensuales")
    comunicacion_afp = fields.Selection([
        ('30', '30 días'), 
        ('60', '60 días')],
        string="Declaración AFP", default="60")
    declaracion_siniestro = fields.Selection([
        ('90', '90 días'), 
        ('120', '120 días')],
        string="Declaración Siniestro", default="120")

    # Recordatorios de Pago
    dias_recordatorio_pago_aviso = fields.Integer(string="Antelación de aviso de Recordatorio de Pago", default=7)
    dias_recordatorio_pago_automatico = fields.Integer(string="Antelación de envío de Recordatorio de Pago automático", default=1)
    recordatorio_pago_automatico = fields.Boolean(string="Recordatorio de Pago Automático", default=False)

    # Prórrogas
    dias_prorroga_aviso = fields.Integer(string="Antelación de aviso de Prórroga", default=7)
    dias_prorroga_automatica = fields.Integer(string="Antelación de comunicación de Prórroga automática", default=89)
    prorroga_automatica = fields.Boolean(string="Comunicación de Prórroga Automática", default=False)

    # AFP
    dias_afp_aviso = fields.Integer(string="Posterioridad de aviso de AFP", default=1)
    dias_afp_automatico = fields.Integer(string="Posterioridad de comunicación de AFP automático", default=59)
    afp_automatico = fields.Boolean(string="Aviso AFP Automático", default=False)

    # Siniestros
    dias_siniestro_aviso = fields.Integer(string="Posterioridad de aviso de Siniestro", default=1)
    dias_siniestro_automatico = fields.Integer(string="Posterioridad de declaración de Siniestro automático", default=119)
    siniestro_automatico = fields.Boolean(string="Aviso Siniestro Automático", default=False)

    # Gestor de Clasificaciones
    ampliacion_automatica = fields.Boolean(string="Ampliación Automática", default=False)
    porcentaje_ampliacion = fields.Float(string="Porcentaje de Variación para Ampliación", default=10.0)

    reduccion_automatica = fields.Boolean(string="Reducción Automática", default=False)
    porcentaje_reduccion = fields.Float(string="Porcentaje de Variación para Reducción", default=50.0)

    eliminacion_automatica = fields.Boolean(string="Eliminación Automática", default=False)
    tiempo_para_eliminar = fields.Integer(string="Días sin facturar para Eliminación", default=365)

    # Declaración de Ventas
    dia_declaracion_ventas = fields.Integer(string="Día del Mes para Declaración de Ventas", default=25)
    variable_minorizacion = fields.Float(string="Porcentaje de Minorización", default=20.0)
    declaracion_ventas_automatica = fields.Boolean(string="Declaración de Ventas Automática", default=False)


    ### FUNCIONES PARA GUARDAR Y RECUPERAR LOS VALORES DE CONFIGURACIÓN ###

    def set_values(self):
        """Guarda los valores configurados en el sistema (ir.config_parameter)"""
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.tipo_poliza', self.tipo_poliza)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.email_agente_asegurador', self.email_agente_asegurador)


        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.capital_asegurado', self.capital_asegurado)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.cifra_anonimos', self.cifra_anonimos)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.capital_interior', self.capital_interior)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.capital_exterior', self.capital_exterior)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.duracion_maxima_credito', self.duracion_maxima_credito)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.declaracion_afp', self.comunicacion_afp)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.declaracion_siniestro', self.declaracion_siniestro)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.declaracion_ventas', self.declaracion_ventas)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.recordatorio_pago_automatico', self.recordatorio_pago_automatico)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_recordatorio_pago_aviso', self.dias_recordatorio_pago_aviso)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_recordatorio_pago_automatico', self.dias_recordatorio_pago_automatico)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_prorroga_aviso', self.dias_prorroga_aviso)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_prorroga_automatica', self.dias_prorroga_automatica)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.prorroga_automatica', self.prorroga_automatica)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_afp_aviso', self.dias_afp_aviso)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_afp_automatico', self.dias_afp_automatico)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.afp_automatico', self.afp_automatico)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_siniestro_aviso', self.dias_siniestro_aviso)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dias_siniestro_automatico', self.dias_siniestro_automatico)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.siniestro_automatico', self.siniestro_automatico)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.ampliacion_automatica', self.ampliacion_automatica)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.porcentaje_ampliacion', self.porcentaje_ampliacion)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.reduccion_automatica', self.reduccion_automatica)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.porcentaje_reduccion', self.porcentaje_reduccion)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.eliminacion_automatica', self.eliminacion_automatica)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.tiempo_para_eliminar', self.tiempo_para_eliminar)

        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.dia_declaracion_ventas', self.dia_declaracion_ventas)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.variable_minorizacion', self.variable_minorizacion)
        self.env['ir.config_parameter'].sudo().set_param('credito_caucion.declaracion_ventas_automatica', self.declaracion_ventas_automatica)

    @api.model
    def get_values(self):
        """Recupera los valores guardados en ir.config_parameter, o asigna los valores predeterminados"""
        res = super(ResConfigSettings, self).get_values()
        param_env = self.env['ir.config_parameter'].sudo()

        res.update({
            'tipo_poliza': param_env.get_param('credito_caucion.tipo_poliza', 'lider'),
            'email_agente_asegurador': param_env.get_param('credito_caucion.email_agente_asegurador', ''),

            'capital_asegurado': int(param_env.get_param('credito_caucion.capital_asegurado', '10000')),
            'cifra_anonimos': int(param_env.get_param('credito_caucion.cifra_anonimos', '5000')),
            'capital_interior': int(param_env.get_param('credito_caucion.capital_interior', '20000')),
            'capital_exterior': int(param_env.get_param('credito_caucion.capital_exterior', '30000')),

            'duracion_maxima_credito': param_env.get_param('credito_caucion.duracion_maxima_credito', '90'),
            'comunicacion_afp': param_env.get_param('credito_caucion.declaracion_afp', '60'),
            'declaracion_siniestro': param_env.get_param('credito_caucion.declaracion_siniestro', '120'),
            'declaracion_ventas': param_env.get_param('credito_caucion.declaracion_ventas', 'mensuales'),

            'recordatorio_pago_automatico': param_env.get_param('credito_caucion.recordatorio_pago_automatico', False),
            'dias_recordatorio_pago_aviso': int(param_env.get_param('credito_caucion.dias_recordatorio_pago_aviso', '7')),
            'dias_recordatorio_pago_automatico': int(param_env.get_param('credito_caucion.dias_recordatorio_pago_automatico', '1')),

            'dias_prorroga_aviso': int(param_env.get_param('credito_caucion.dias_prorroga_aviso', '7')),
            'dias_prorroga_automatica': int(param_env.get_param('credito_caucion.dias_prorroga_automatica', '89')),
            'prorroga_automatica': param_env.get_param('credito_caucion.prorroga_automatica', False),

            'dias_afp_aviso': int(param_env.get_param('credito_caucion.dias_afp_aviso', '1')),
            'dias_afp_automatico': int(param_env.get_param('credito_caucion.dias_afp_automatico', '59')),
            'afp_automatico': param_env.get_param('credito_caucion.afp_automatico', False),

            'dias_siniestro_aviso': int(param_env.get_param('credito_caucion.dias_siniestro_aviso', '1')),
            'dias_siniestro_automatico': int(param_env.get_param('credito_caucion.dias_siniestro_automatico', '119')),
            'siniestro_automatico': param_env.get_param('credito_caucion.siniestro_automatico', False),

            'ampliacion_automatica': param_env.get_param('credito_caucion.ampliacion_automatica', False),
            'porcentaje_ampliacion': float(param_env.get_param('credito_caucion.porcentaje_ampliacion', '10.0')),

            'reduccion_automatica': param_env.get_param('credito_caucion.reduccion_automatica', False),
            'porcentaje_reduccion': float(param_env.get_param('credito_caucion.porcentaje_reduccion', '50.0')),

            'eliminacion_automatica': param_env.get_param('credito_caucion.eliminacion_automatica', False),
            'tiempo_para_eliminar': int(param_env.get_param('credito_caucion.tiempo_para_eliminar', '365')),

            'dia_declaracion_ventas': int(param_env.get_param('credito_caucion.dia_declaracion_ventas', '25')),
            'variable_minorizacion': float(param_env.get_param('credito_caucion.variable_minorizacion', '20.0')),
            'declaracion_ventas_automatica': param_env.get_param('credito_caucion.declaracion_ventas_automatica', False),
        })

        return res

