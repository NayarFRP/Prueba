# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    refund_journal_id = fields.Many2one('account.journal', string='Diario de reembolso')
