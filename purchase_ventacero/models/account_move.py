# -*- coding: utf-8 -*-
from odoo import models, fields, Command, api, tools, _
from odoo.tools.float_utils import float_repr
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    xml_check = fields.Boolean(string="Validacion de XML", default=True)


    def action_post(self):
        if self.move_type == 'in_invoice':
            if self.xml_check:
                if not self.l10n_mx_edi_cfdi_uuid:
                    raise ValidationError(_("No se ha adjuntado el XML de la factura"))
                if self.l10n_mx_edi_cfdi_amount != self.amount_total:
                    raise ValidationError(_("El total de la factura no coincide con el del XML"))
                if self.partner_id.vat != self.l10n_mx_edi_cfdi_supplier_rfc:
                    raise ValidationError(_("El RFC en el XML no correcponde al del proveedor capturado en la factura"))

                facturas = self.sudo().env['account.move'].search_count([('l10n_mx_edi_cfdi_uuid', '=', self.l10n_mx_edi_cfdi_uuid)])
                if facturas > 1:
                    raise ValidationError(_("Ya se utilizo el XML en otra factura"))


        return super(AccountMove, self).action_post()
        