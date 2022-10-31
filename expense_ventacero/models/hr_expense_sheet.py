# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.tools import email_split, float_is_zero, float_repr
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import clean_context, format_date
import logging

_logger = logging.getLogger(__name__)

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    petty_cash_id = fields.Many2one('account.journal', string='Caja chica')
    refund_id = fields.Many2one('account.payment', string='Reembolso')

    def action_sheet_move_create(self):
        samples = self.mapped('expense_line_ids.sample')
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({'state': 'post'})
            return

        if any(sheet.state != 'approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Specify expense journal to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.with_context(clean_context(self.env.context)).action_move_create()
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(lambda sheet: sheet.payment_mode != 'company_account' and sheet.expense_line_ids)
        to_post.write({'state': 'post'})
        (self - to_post).write({'state': 'done'})
        self.activity_update()
        return res


    def create_refund(self):
        return {
                "type": "ir.actions.act_window",
                "res_model": "account.payment",
                "views": [[False, "form"]],
                "context": {'default_is_internal_transfer': True, 'default_payment_type': 'outbound', 
                'default_amount': self.total_amount, 'default_ref': self.name, 'default_journal_id': self.petty_cash_id.refund_journal_id.id,
                'default_destination_journal_id': self.petty_cash_id.id, 'default_l10n_mx_edi_payment_method_id': self.petty_cash_id.refund_journal_id.l10n_mx_edi_payment_method_id.id,
                'active_model': 'hr.expense.sheet'},
            }


    def action_view_refund(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "views": [[False, "form"]],
            "res_id": self.refund_id.id,
            "context": {"create": False},
            }


    @api.onchange('employee_id')
    def get_supplier_id(self):
        for move in self:
            move.petty_cash_id = move.employee_id.petty_cash_id.id


    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.account_move_id.ids,
                'default_partner_bank_id': self.employee_id.sudo().bank_account_id.id,
                'default_journal_id': self.petty_cash_id.id,
                'default_l10n_mx_edi_payment_method_id': self.petty_cash_id.l10n_mx_edi_payment_method_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def action_create_refund_view(self):
        total_amount = 0
        user_id = 0
        ref = ""
        journal_id = 0
        destination_journal_id = 0
        mx_edi_payment_method_id = 0

        for informe in self.ids:
            informe_actual = self.sudo().env['hr.expense.sheet'].search([('id', '=', informe)])
            if informe_actual:
                if user_id == 0:
                    user_id = informe_actual.employee_id.id
                else:
                    if user_id != informe_actual.employee_id.id:
                        raise ValidationError(_("Solo puedes reembolsar informes del mismo empleado"))

                total_amount += informe_actual.total_amount
                ref += str(informe_actual.name) + " - "

                if journal_id == 0:
                    journal_id = informe_actual.petty_cash_id.refund_journal_id.id

                if destination_journal_id == 0:
                    destination_journal_id = informe_actual.petty_cash_id.id

                if mx_edi_payment_method_id == 0:
                    mx_edi_payment_method_id = informe_actual.petty_cash_id.refund_journal_id.l10n_mx_edi_payment_method_id.id

        
        return {
                "type": "ir.actions.act_window",
                "res_model": "account.payment",
                "views": [[False, "form"]],
                "context": {'default_is_internal_transfer': True, 'default_payment_type': 'outbound', 
                'default_amount': total_amount, 'default_ref': ref, 'default_journal_id': journal_id,
                'default_destination_journal_id': destination_journal_id, 'default_l10n_mx_edi_payment_method_id': mx_edi_payment_method_id,
                'active_ids': self.ids, 'active_model': 'hr.expense.sheet'},
            }
            