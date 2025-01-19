from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Policy Configurations
    policy_type = fields.Selection([
        ('lider', 'Líder'),
        ('lider+', 'Líder +'), 
        ('bonus', 'Bonus'),
        ('start', 'Start'),
        ('agil', 'Ágil')], 
        string="Tipo de Póliza", default="lider")
    insurance_agent_email = fields.Char(string="Correo del Agente")
    
    aws_email = fields.Char(string="Correo electrónico para configurar en AWS SES", help="Correo que será verificado para enviar emails mediante AWS SES.")
    aws_email_verified = fields.Boolean(string="¿Correo Verificado?", readonly=True, help="Indica si el correo fue verificado correctamente con AWS SES.")

    # Capital 
    capital_insured = fields.Integer(string="Capital Asegurado")
    capital_anonymous = fields.Integer(string="Capital Anónimos")
    capital_interior = fields.Integer(string="Capital Interior")
    capital_exterior = fields.Integer(string="Capital Exterior")

    # Durations 
    max_credit_duration = fields.Selection([
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
    sales_declaration = fields.Selection([
        ('mensuales', 'Mensuales'),
        ('trimestrales', 'Trimestrales'),
        ('anuales', 'Anuales')],
        string="Declaración de Ventas", default="mensuales")
    afp_communication = fields.Selection([
        ('30', '30 días'), 
        ('60', '60 días')],
        string="Declaración AFP", default="60")
    claim_declaration = fields.Selection([
        ('90', '90 días'), 
        ('120', '120 días')],
        string="Declaración Siniestro", default="120")

    payment_reminder_notice_days = fields.Integer(string="Antelación de aviso de Recordatorio de Pago", default=7)
    automatic_payment_reminder_days = fields.Integer(string="Antelación de envío de Recordatorio de Pago automático", default=1)
    automatic_payment_reminder = fields.Boolean(string="Recordatorio de Pago Automático", default=False)

    extension_notice_days = fields.Integer(string="Antelación de aviso de Prórroga", default=7)
    automatic_extension_days = fields.Integer(string="Antelación de comunicación de Prórroga automática", default=89)
    automatic_extension = fields.Boolean(string="Comunicación de Prórroga Automática", default=False)

    afp_notice_days = fields.Integer(string="Posterioridad de aviso de AFP", default=1)
    automatic_afp_days = fields.Integer(string="Posterioridad de comunicación de AFP automático", default=59)
    automatic_afp = fields.Boolean(string="Aviso AFP Automático", default=False)

    claim_notice_days = fields.Integer(string="Posterioridad de aviso de Siniestro", default=1)
    automatic_claim_days = fields.Integer(string="Posterioridad de declaración de Siniestro automático", default=119)
    automatic_claim = fields.Boolean(string="Aviso Siniestro Automático", default=False)

    automatic_review = fields.Boolean(string="Revisión Automática", default=False)
    review_percentage = fields.Float(string="Porcentaje de Variación para Revisión", default=0.0)

    automatic_extension = fields.Boolean(string="Ampliación Automática", default=False)
    extension_percentage = fields.Float(string="Porcentaje de Variación para Ampliación", default=10.0)

    automatic_reduction = fields.Boolean(string="Reducción Automática", default=False)
    reduction_percentage = fields.Float(string="Porcentaje de Variación para Reducción", default=50.0)

    automatic_deletion = fields.Boolean(string="Eliminación Automática", default=False)
    days_to_delete = fields.Integer(string="Días sin facturar para Eliminación", default=365)

    sales_declaration_day = fields.Integer(string="Día del Mes para Declaración de Ventas", default=25)
    automatic_sales_declaration = fields.Boolean(string="Declaración de Ventas Automática", default=False)


    def action_verify_email(self):
        print("hola")
        return

    def update_verification_status(self):
        return


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        param.set_param('credito_caucion.policy_type', self.policy_type)
        param.set_param('credito_caucion.insurance_agent_email', self.insurance_agent_email)

        param.set_param('credito_caucion.capital_insured', self.capital_insured)
        param.set_param('credito_caucion.capital_anonymous', self.capital_anonymous)
        param.set_param('credito_caucion.capital_interior', self.capital_interior)
        param.set_param('credito_caucion.capital_exterior', self.capital_exterior)

        param.set_param('credito_caucion.max_credit_duration', self.max_credit_duration)
        param.set_param('credito_caucion.afp_communication', self.afp_communication)
        param.set_param('credito_caucion.claim_declaration', self.claim_declaration)
        param.set_param('credito_caucion.sales_declaration', self.sales_declaration)

        param.set_param('credito_caucion.automatic_payment_reminder', self.automatic_payment_reminder)
        param.set_param('credito_caucion.payment_reminder_notice_days', self.payment_reminder_notice_days)
        param.set_param('credito_caucion.automatic_payment_reminder_days', self.automatic_payment_reminder_days)

        param.set_param('credito_caucion.extension_notice_days', self.extension_notice_days)
        param.set_param('credito_caucion.automatic_extension_days', self.automatic_extension_days)
        param.set_param('credito_caucion.automatic_extension', self.automatic_extension)

        param.set_param('credito_caucion.afp_notice_days', self.afp_notice_days)
        param.set_param('credito_caucion.automatic_afp_days', self.automatic_afp_days)
        param.set_param('credito_caucion.automatic_afp', self.automatic_afp)

        param.set_param('credito_caucion.claim_notice_days', self.claim_notice_days)
        param.set_param('credito_caucion.automatic_claim_days', self.automatic_claim_days)
        param.set_param('credito_caucion.automatic_claim', self.automatic_claim)

        param.set_param('credito_caucion.automatic_extension', self.automatic_extension)
        param.set_param('credito_caucion.extension_percentage', self.extension_percentage)

        param.set_param('credito_caucion.automatic_reduction', self.automatic_reduction)
        param.set_param('credito_caucion.reduction_percentage', self.reduction_percentage)

        param.set_param('credito_caucion.automatic_deletion', self.automatic_deletion)
        param.set_param('credito_caucion.days_to_delete', self.days_to_delete)

        param.set_param('credito_caucion.sales_declaration_day', self.sales_declaration_day)
        param.set_param('credito_caucion.automatic_sales_declaration', self.automatic_sales_declaration)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_env = self.env['ir.config_parameter'].sudo()

        res.update({
            'policy_type': param_env.get_param('credito_caucion.policy_type', 'lider'),
            'insurance_agent_email': param_env.get_param('credito_caucion.insurance_agent_email', ''),

            'capital_insured': int(param_env.get_param('credito_caucion.capital_insured', '10000')),
            'capital_anonymous': int(param_env.get_param('credito_caucion.capital_anonymous', '5000')),
            'capital_interior': int(param_env.get_param('credito_caucion.capital_interior', '20000')),
            'capital_exterior': int(param_env.get_param('credito_caucion.capital_exterior', '30000')),

            'max_credit_duration': param_env.get_param('credito_caucion.max_credit_duration', '90'),
            'afp_communication': param_env.get_param('credito_caucion.afp_communication', '60'),
            'claim_declaration': param_env.get_param('credito_caucion.claim_declaration', '120'),
            'sales_declaration': param_env.get_param('credito_caucion.sales_declaration', 'mensuales'),

            'automatic_payment_reminder': param_env.get_param('credito_caucion.automatic_payment_reminder', False),
            'payment_reminder_notice_days': int(param_env.get_param('credito_caucion.payment_reminder_notice_days', '7')),
            'automatic_payment_reminder_days': int(param_env.get_param('credito_caucion.automatic_payment_reminder_days', '1')),

            'extension_notice_days': int(param_env.get_param('credito_caucion.extension_notice_days', '7')),
            'automatic_extension_days': int(param_env.get_param('credito_caucion.automatic_extension_days', '89')),
            'automatic_extension': param_env.get_param('credito_caucion.automatic_extension', False),

            'afp_notice_days': int(param_env.get_param('credito_caucion.afp_notice_days', '1')),
            'automatic_afp_days': int(param_env.get_param('credito_caucion.automatic_afp_days', '59')),
            'automatic_afp': param_env.get_param('credito_caucion.automatic_afp', False),

            'claim_notice_days': int(param_env.get_param('credito_caucion.claim_notice_days', '1')),
            'automatic_claim_days': int(param_env.get_param('credito_caucion.automatic_claim_days', '119')),
            'automatic_claim': param_env.get_param('credito_caucion.automatic_claim', False),

            'automatic_extension': param_env.get_param('credito_caucion.automatic_extension', False),
            'extension_percentage': float(param_env.get_param('credito_caucion.extension_percentage', '10.0')),

            'automatic_reduction': param_env.get_param('credito_caucion.automatic_reduction', False),
            'reduction_percentage': float(param_env.get_param('credito_caucion.reduction_percentage', '50.0')),

            'automatic_deletion': param_env.get_param('credito_caucion.automatic_deletion', False),
            'days_to_delete': int(param_env.get_param('credito_caucion.days_to_delete', '365')),

            'sales_declaration_day': int(param_env.get_param('credito_caucion.sales_declaration_day', '25')),
            'automatic_sales_declaration': param_env.get_param('credito_caucion.automatic_sales_declaration', False),
        })
        return res
