# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountCashControl(models.Model):
    _name = 'account.cash.control'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    _description = 'Control de caja'

    name = fields.Char('Nombre', copy=False, index=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('open', 'Abierto'),
        ('closing', 'Control de cierre'),
        ('close', 'Cerrado'),
    ], string='Estado', tracking=True, default='draft')
    team_id = fields.Many2one('crm.team', string='Sucursal', default=lambda self: self.env.user.team_id)
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user)
    date = fields.Date('Fecha')
    date_begin = fields.Datetime('Fecha de apertura')
    date_end = fields.Datetime('Fecha de cierre')

    account_cash_control_balance_id = fields.One2many('account.cash.control.balance', 'cash_control_id', string="Saldo")
    account_cash_control_operations_id = fields.One2many('account.cash.control.operations', 'cash_control_id', string="Operaciones")
    account_cash_control_transfers_id = fields.One2many('account.cash.control.transfers', 'cash_control_id', string="Transferencias")
    account_cash_control_close_id = fields.One2many('account.cash.control.close', 'cash_control_id', string="Transferencias")

    diference_total = fields.Float('Diferencia', compute='_compute_diference_total')
    allow_close = fields.Boolean(string="Permitir cierre")


    @api.model
    def create(self, vals):
        sequence_code = self.env.user.team_id.sequence_id.code
        _logger.info('############' + str(sequence_code))


        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code(sequence_code) or _('New')

        result = super(AccountCashControl, self).create(vals)

        journal_ids = self.sudo().env['account.journal'].search([('team_id', '=', result.team_id.id)])
        for journal in journal_ids:
            values = {
                'cash_control_id': result.id,
                'journal_id': journal.id,
                'initial_balance': 0,
                'sale_balance': 0,
                'in_balance': 0,
                'out_balance': 0,
            }
            balance_line = self.sudo().env['account.cash.control.balance'].create(values)
        
        return result

    @api.depends('account_cash_control_close_id.counted_amount')
    def _compute_diference_total(self):
        total = 0
        for reg in self:
            for line in reg.account_cash_control_close_id:
                total += line.diference

            reg.update({
                'diference_total': total,
            })


    def cash_control_open(self):
        return {
            'res_model': 'wizard.cash.control.open',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.cash.control',
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }


    def cash_control_close_1(self):
        for reg in self:
            for line in reg.account_cash_control_balance_id:
                if line.journal_id.type == 'cash':
                    values = {
                        'cash_control_id': reg.id,
                        'journal_id': line.journal_id.id,
                        'expected_amount': line.ending_balance,
                    }
                    close_line = self.sudo().env['account.cash.control.close'].create(values)
        self.update({
            'state': 'closing'
        })


    def cash_control_close_2(self):
        return {
            'res_model': 'wizard.cash.control.close',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.cash.control',
                'active_id': self.id,
                'default_team_id': self.team_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }


    def cash_control_out(self):
        return {
            'res_model': 'wizard.cash.control.out',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.cash.control',
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }


    def cash_control_in(self):
        return {
            'res_model': 'wizard.cash.control.in',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.cash.control',
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
            }
  
  