# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleApprover(models.Model):
    _name = 'sale.approver'
    _description = 'Sale approver'

    _check_company_auto = True

    user_id = fields.Many2one('res.users', string="User", required=True, check_company=True)
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new", readonly=True)
    request_id = fields.Many2one('sale.order', string="Request",
        ondelete='cascade', check_company=True)
    company_id = fields.Many2one(
        string='Company', related='request_id.company_id',
        store=True, readonly=True, index=True)

    def action_approve(self):
        self.request_id.action_approve(self)

    def action_refuse(self):
        self.request_id.action_refuse(self)

    def _create_activity(self):
        for approver in self:
            approver.request_id.activity_schedule(
                'credit_ventacero.mail_activity_data_sale_approval',
                user_id=approver.user_id.id)
