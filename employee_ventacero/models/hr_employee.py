# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, tools, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tipo_sangre = fields.Char(string="Tipo de sangre")
    alergias = fields.Char(string="Alergias y/o Enfermedades")
    numero_seguro = fields.Char(string="Número de seguro social IMSS")
    clinica_imss = fields.Char(string="Clinica del IMSS")

    info_padre = fields.Text(string="Informacion del Padre")
    info_madre = fields.Text(string="Informacion de la Madre")
    info_conyuge = fields.Text(string="Informacion del Cónyuge")
    info_hijos = fields.Text(string="Informacion de los Hijos")

    fecha_ingreso = fields.Date(string="Fecha de ingreso")
    salario_diario = fields.Float(string="Salario diaro")
    salario_integrado = fields.Float(string="Salario diario integrado")
    