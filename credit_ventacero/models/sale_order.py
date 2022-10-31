# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_credit = fields.Monetary(related='partner_id.commercial_partner_id.credit', readonly=True)
    partner_credit_limit = fields.Monetary(related='partner_id.credit_limit_compute', readonly=True)
    show_partner_credit_warning = fields.Boolean(compute='_compute_show_partner_credit_warning')
    credit_limit_type = fields.Selection(related='company_id.credit_limit_type')

    allow_sale = fields.Boolean(string="Permitir venta", default=True)
    credit_due_days = fields.Integer(related='partner_id.credit_due_days')
    percentage_exceeded = fields.Float(string='Porcentaje excedido')
    approval_group = fields.Char(string="Grupo de aprobación")

    approval_button = fields.Boolean('Boton de aprobación', default=False)
    approval_line = fields.Many2one('approval.criteria', string="Linea de aprobación")
    approver_ids = fields.One2many('sale.approver', 'request_id', string="Approvers", check_company=True)
    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status")

    @api.depends('approver_ids.status')
    def _compute_user_status(self):
        for approval in self:
            approval.user_status = approval.approver_ids.filtered(lambda approver: approver.user_id == self.env.user).status

    def action_approval_request(self):
        for record in self.approver_ids:
            self.write({'approver_ids': [(2,record.id)]})

        approver_ids = []
        for group in self.approval_line.groups:
            for user in group.users:
                if user.id not in approver_ids:
                    approver_ids.append(user.id)

        for line in approver_ids:
            values = {
                'user_id':line,
                'status': 'new',
                'request_id': self.id,
            }
            new_approver = self.env['sale.approver'].create(values)

        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        approvers._create_activity()
        approvers.write({'status': 'pending'})
        self.approval_button = False

    def _get_user_approval_activities(self, user):
        domain = [
            ('res_model', '=', 'sale.order'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', self.env.ref('credit_ventacero.mail_activity_data_sale_approval').id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    def action_approve(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'approved'})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        self.approval_button = False
        self.allow_sale = True
        self.message_post(body="<span class='fa fa-thumbs-o-up fa-fw'></span> Venta aprobada")

    def action_refuse(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'refused'})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        self.approval_button = True
        self.allow_sale = False
        self.message_post(body="<span class='fa fa-thumbs-o-down fa-fw'></span> Venta rechazada")



    @api.depends('partner_credit_limit', 'partner_credit', 'order_line',
                 'company_id.account_default_credit_limit', 'company_id.account_credit_limit')
    def _compute_show_partner_credit_warning(self):
        for order in self:
            account_credit_limit = order.company_id.account_credit_limit
            company_limit = order.partner_credit_limit == -1 and order.company_id.account_default_credit_limit
            partner_limit = order.partner_credit_limit + order.amount_total > 0 and order.partner_credit_limit
            partner_credit = order.partner_credit + order.amount_total
            order.show_partner_credit_warning = account_credit_limit and \
                                                ((company_limit and partner_credit > company_limit) or \
                                                (partner_limit and partner_credit > partner_limit))

            if order.partner_credit_limit:
                if partner_credit > order.partner_credit_limit:
                    percentage_exceeded_aux = ((partner_credit - order.partner_credit_limit) * 100)/order.partner_credit_limit
                    
                    if percentage_exceeded_aux > 100:
                        order.percentage_exceeded = 100
                    else:
                        order.percentage_exceeded = percentage_exceeded_aux
                else:
                    order.percentage_exceeded = 0
            

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for so in self:
            if not so.allow_sale:
                raise ValidationError(_("Cotización no aprobada"))
        return result


    @api.onchange('show_partner_credit_warning', 'credit_due_days', 'order_line')
    def _onchange_credit_fields(self):
        if self.show_partner_credit_warning or self.credit_due_days > 0:
            self.update({
                'allow_sale': False,
                'approval_button': True,
            })
            if self.percentage_exceeded == 0:
                linea = self.get_approval_group(self.credit_due_days, self.partner_id.comportamiento_pago, -1)
                if linea:
                    self.update({
                        'approval_group': linea.groups_name,
                        'approval_line': linea.id,
                    })
                else:
                    self.update({
                        'allow_sale': True,
                        'approval_button': False,
                    })
            else:
                linea = self.get_approval_group(self.credit_due_days, self.partner_id.comportamiento_pago, self.percentage_exceeded)
                if linea:
                    self.update({
                        'approval_group': linea.groups_name,
                        'approval_line': linea.id,
                    })
                else:
                    self.update({
                        'allow_sale': True,
                        'approval_button': False,
                    })
        else:
            self.update({
                'allow_sale': True,
                'approval_button': False,
            })

    
    def get_approval_group(self, vencimiento, comportamiento, porcentaje):
        if porcentaje == -1:
            _logger.info('VALORES: 1: ' + str(vencimiento) + " 2: " + str(comportamiento) + " 3: " + str(porcentaje))
            linea = self.env['approval.criteria'].search([('vencimiento_inicial', '<', vencimiento), ('vencimiento_final', '>=', vencimiento),('comportamiento_pago', '=', comportamiento),('excedente_inicial', '=', porcentaje),('excedente_final', '=', porcentaje)])[0] if self.env['approval.criteria'].search([('vencimiento_inicial', '<', vencimiento), ('vencimiento_final', '>=', vencimiento),('comportamiento_pago', '=', comportamiento),('excedente_inicial', '=', porcentaje),('excedente_final', '=', porcentaje)]) else False
            _logger.info('LINEA: ' + str(linea))
        else:
            _logger.info('VALORES: 1: ' + str(vencimiento) + " 2: " + str(comportamiento) + " 3: " + str(porcentaje))
            linea = self.env['approval.criteria'].search([('vencimiento_inicial', '<', vencimiento), ('vencimiento_final', '>=', vencimiento),('comportamiento_pago', '=', comportamiento),('excedente_inicial', '<', porcentaje),('excedente_final', '>=', porcentaje)])[0] if self.env['approval.criteria'].search([('vencimiento_inicial', '<', vencimiento), ('vencimiento_final', '>=', vencimiento),('comportamiento_pago', '=', comportamiento),('excedente_inicial', '<', porcentaje),('excedente_final', '>=', porcentaje)]) else False
            _logger.info('LINEA: ' + str(linea))

        return linea

