# -*- coding: utf-8 -*-
from odoo import models, api, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        result = []
        for rec in self:
            name = '%s' % (rec.default_code)
            result.append((rec.id, name))
        return result

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.name
        if self.description_sale:
            name += '\n' + self.description_sale

        return name
