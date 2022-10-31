# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    team_id = fields.Many2one('crm.team', string='Sucursal')
    caja_retiro = fields.Boolean(string="Caja de retiro")
    deposit_journal = fields.Many2one('account.journal', string='Diario de deposito')
