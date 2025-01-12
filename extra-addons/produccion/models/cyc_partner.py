from odoo import models, fields, api

class CycPartner(models.Model):
    _name = 'cyc.partner'
    _description = 'CyC Client'
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'cyc.api.mixin']

    # RELATIONS

    cyc_contact_ids = fields.One2many('cyc.contact', 'cyc_partner_id', string='Sucursales')
    cyc_collection_ids = fields.One2many('cyc.collection', 'cyc_partner_id', string='CyC Cobros')
    cyc_classification_ids = fields.One2many('cyc.classification', 'cyc_partner_id', string='Clasificaciones')
    cyc_afp_ids = fields.One2many('cyc.afp', 'cyc_partner_id', string='AFPs')
    cyc_extension_ids = fields.One2many('cyc.extension', 'cyc_partner_id', string='Prórrogas')
    cyc_claim_ids = fields.One2many('cyc.claim', 'cyc_partner_id', string='Siniestros')
    cyc_alert_ids = fields.One2many('cyc.alert', 'cyc_partner_id', string='Alertas')
    cyc_result_ids = fields.One2many('cyc.result', 'cyc_partner_id', string='Resultados')

    #sale_order_ids = fields.One2many('cyc.sale.order.mapping', 'cyc_partner_id', string='Pedidos de Venta') 
    #puedo hacerlo con el cyc contact

    currency_id = fields.Many2one('res.currency', string="Moneda")

    # FIELDS

    name = fields.Char(string="Razón Social")
    vat = fields.Char(string="NIF/VAT", unique=True) 
    cyc_code = fields.Integer(string="Expediente", unique=True)
    
    country_id = fields.Many2one('res.country', string="País")
    state_id = fields.Many2one('res.country.state', string="Provincia")
    
    cnae = fields.Char(string='CNAE') # COMBO DE CNAE Y DESCRIPCION CNAE
    sector = fields.Char(string='Sector')

    antiquity = fields.Integer(string='Antigüedad (años)')
    intensity = fields.Selection(selection=[
        ('0', 'Nula'),
        ('1', 'Básica'),
        ('2', 'Mediana'),
        ('3', 'Intensa'),
        ('4', 'Muy Intensa')
    ], string='Intensidad', default='0')

    payment_velocity = fields.Selection(selection=[
        ('0', 'Muy Lenta'),
        ('1', 'Lenta'),
        ('2', 'Normal'),
        ('3', 'Rápida'),
        ('4', 'Muy Rápida')
    ], string='Velocidad de Pago', default='0')
    compliance_with_deadlines = fields.Selection(selection=[
        ('0', 'Nula'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy Alta'),
    ], string='Cumplimiento de Plazos', default='0')
    ability_to_communicate = fields.Selection(selection=[
        ('0', 'Nula'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy Alta'),
    ], string='Capacidad de Comunicación', default='0')

    client_nature = fields.Selection(selection=[
        ('00', 'Asegurables'),
        ('01', 'Organismos Públicos'),
        ('02', 'Empresas Vinculadas'),
        ('03-I', 'Exportación'),
        ('03-E', 'Mercado Interior'),
        ('04', 'Particulares'),
        ('05', 'Contado'),
        ('06', 'Clasificado nada'),
        ('07', 'Otros'),
        ('08', 'Paises sin Cobertura')
    ], string='Naturaleza del Cliente', default='00')

    invoiced_last_period = fields.Monetary("Billed Last Period", currency_field='currency_id', default=0)
    last_order_date = fields.Date(string="Last Order Date")
    default_sales_duration = fields.Selection([
        ('30', '30 días'),
        ('60', '60 días'),
        ('90', '90 días'),
        ('120', '120 días'),
        ('150', '150 días'),
        ('180', '180 días'),
    ], string='Duración de Ventas Predeterminada', default='30')
    classification_status = fields.Selection([
        ('to classify', 'Para Clasificar'),
        ('to amplify', 'Para Ampliar'),
        ('to reduce', 'Para Reducir'),
        ('to remove', 'Para Eliminar'),
        ('to review', 'Para Revisar'),
        ('limited', 'Limitado'),
        ('classified', 'Clasificado'),
        ('not classified', 'No Clasificado'),
        ('pending', 'Pendiente'),
    ], string="Classification Status", default='not classified')

    number_open_afps = fields.Integer(string='# de AFPs', default=0)
    number_open_extensions = fields.Integer(string='# de Prórrogas', default=0)
    number_open_claim = fields.Integer(string='# de Siniestros', default=0)
    number_alerts = fields.Integer(string='# de Alertas', default=0)

    number_cyc_collections = fields.Integer(string="# de Facturas", default=0)
    number_cyc_contacts = fields.Integer(string="# de Sucursales", default=1)

    amount_classification_requested = fields.Monetary(string='Importe Solicitado', currency_field='currency_id', default=0)
    amount_classification_granted = fields.Monetary(string='Importe Concedido', currency_field='currency_id', default=0)
    amount_open_afps = fields.Monetary(string='Importe AFPs', currency_field='currency_id', default=0)
    amount_open_extensions = fields.Monetary(string='Importe Prórrogas', currency_field='currency_id', default=0)
    amount_open_claim = fields.Monetary(string='Importe Siniestro', currency_field='currency_id', default=0)

    total_invoiced = fields.Monetary(string="Total Facturado", currency_field='currency_id', default=0)
    living_balance = fields.Monetary(string="Saldo Vivo", currency_field='currency_id', default=0)
    amount_on_time = fields.Monetary(string="Dentro de Plazo", currency_field='currency_id', default=0)
    amount_overdue = fields.Monetary(string="Fuera de Plazo", currency_field='currency_id', default=0)

    # DOMAIN-BASED FIELDS

    classification_ids = fields.One2many('cyc.classification', 'cyc_partner_id', domain=[('status1', '=', 'in force')])
    classifications_historic_ids = fields.One2many('cyc.classification', 'cyc_partner_id', domain=[('status1', '=', 'historic')])

    afp_open_ids = fields.One2many('cyc.afp', 'cyc_partner_id', domain=[('status1', '=', 'open')])
    afp_historic_ids = fields.One2many('cyc.afp', 'cyc_partner_id', domain=[('status1', '=', 'historic')])

    extension_open_ids = fields.One2many('cyc.extension', 'cyc_partner_id', domain=[('status1', '=', 'open')])
    extension_historic_ids = fields.One2many('cyc.extension', 'cyc_partner_id', domain=[('status1', '=', 'historic')])

    claim_open_ids = fields.One2many('cyc.claim', 'cyc_partner_id', domain=[('status1', '=', 'open')])
    claim_historic_ids = fields.One2many('cyc.claim', 'cyc_partner_id', domain=[('status1', '=', 'historic')])

    alert_new_ids = fields.One2many('cyc.alert', 'cyc_partner_id', domain=[('status', '=', 'new')])
    alert_historic_ids = fields.One2many('cyc.alert', 'cyc_partner_id', domain=[('status', '=', 'historic')])

    result_last_ids = fields.One2many('cyc.result', 'cyc_partner_id', domain=[('status', '=', 'last')])
    result_historic_ids = fields.One2many('cyc.result', 'cyc_partner_id', domain=[('status', '=', 'historic')])

    # SEARCH FIELDS

    incidents_number = fields.Integer(string='# de Incidencia')
    high_risk_alerts_number = fields.Integer(string='# de Alertas de Alto Riesgo')
    medium_risk_alerts_number = fields.Integer(string='# de Alertas de Riesgo Medio')

    # -------
    # METHODS
    # -------

    def action_view_res_partner(self):
        return

    def action_open_classification_wizard(self):
        return
