from odoo import models, fields

class CycContact(models.Model):
    _name = 'cyc.contact'
    _description = 'CyC Contact'
    _order = "name"

    cyc_partner_id = fields.Many2one('cyc.partner', string='Cliente CyC', ondelete='restrict')
    res_partner_id = fields.Many2one('res.partner', string='Sucursal', ondelete='restrict', unique=True)
    cyc_collection_ids = fields.One2many('cyc.collection', 'cyc_contact_id', string='Cobros')

    country_id = fields.Many2one('res.country', string='País', related='res_partner_id.country_id', store=True)
    state_id = fields.Many2one('res.country.state', string='Província', related='res_partner_id.state_id', store=True)
    city = fields.Char(string='Ciudad', related='res_partner_id.city', store=True)
    person = fields.Char(string='Persona de Contacto')
    position = fields.Char(string='Cargo')
    email = fields.Char(string='Email para Recobros')
    phone = fields.Char(string='Teléfono para Recobros')