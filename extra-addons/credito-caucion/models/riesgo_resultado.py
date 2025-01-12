# models/riesgo_resultado.py
from odoo import models, fields

class RiesgoResultado(models.Model):
    _name = 'riesgo.resultado'
    _description = 'Resultado de Riesgo'

    riesgo_id = fields.Many2one('riesgo', string='Riesgo', ondelete='cascade', required=True)
    
    ejercicio = fields.Integer(string='Año del Ejercicio') # Año del Resultado
    ventas = fields.Float(string='Ventas')
    resultado = fields.Float(string='Resultado')
    fondos_propios = fields.Float(string='Fondos Propios')
    fondos_maniobra = fields.Float(string='Fondos de Maniobra')
    endeudamiento_cp = fields.Float(string='Endeudamiento CP')
    empleados = fields.Integer(string='Empleados')
    descripcion_cnae = fields.Char(string='Descripción CNAE')
    etiquetas = fields.Char(string='Etiquetas')
    importe_concedido = fields.Float(string='Importe Concedido')
    importe_solicitado = fields.Float(string='Importe Solicitado')
    num_afp = fields.Integer(string='Número AFP')
    num_pro = fields.Integer(string='Número PRO')
    num_sin = fields.Integer(string='Número SIN')