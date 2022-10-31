# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ApprovalCriteria(models.Model):
    _name = 'approval.criteria'
    _description = 'Criterios de aprobación'

    name = fields.Char("Nombre")
    vencimiento_inicial = fields.Integer('Días de vencimiento inicial')
    vencimiento_final = fields.Integer('Días de vencimiento final')
    comportamiento_pago = fields.Selection([('excelente', 'Excelente'), ('bueno', 'Bueno'), ('regular', 'Regular'), ('moroso', 'Moroso')], string="Comportamiento de pago")
    excedente_inicial = fields.Float('Excedente inicial')
    excedente_final = fields.Float('Excedente final')
    groups_name = fields.Char("Nombre grupos")
    groups = fields.Many2many('res.groups', string='Grupos de permisos')
