# -*- coding: utf-8 -*-
from odoo import models, api, fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    sequence_id = fields.Many2one('ir.sequence', string='Sequencia')
    max_diference = fields.Float(string="Diferencia permitida")
