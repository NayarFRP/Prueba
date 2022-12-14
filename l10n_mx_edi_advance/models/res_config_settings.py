
from odoo import fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_edi_product_advance_id = fields.Many2one(
        'product.product', 'Advance product', readonly=False,
        related='company_id.l10n_mx_edi_product_advance_id',
        help='This product will be used in the advance invoices that are '
        'created automatically when is registered a payment without documents '
        'related or with a difference in favor of the customer.')
    l10n_mx_edi_advance = fields.Selection(
        string='Process for Advances', readonly=False,
        related='company_id.l10n_mx_edi_advance', help='Process to be used in '
        'the advance generation. Based on the GuiaAnexo20 Document.')

    def execute(self):
        self.ensure_one()
        msg = ''
        if self.l10n_mx_edi_advance == 'B' and not 'l10n_mx_edi_total_discount' in self.env[  # noqa
                'account.move.line']._fields:
            msg += _('To allow use the process "B" for advances is necessary '
                     'install the module "l10n_mx_edi_discount".')
        if msg:
            raise UserError(msg)
        return super().execute()
