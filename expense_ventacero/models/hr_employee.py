# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    petty_cash_id = fields.Many2one('account.journal', string='Caja chica')
