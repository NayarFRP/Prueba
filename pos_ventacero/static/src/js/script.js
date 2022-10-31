odoo.define('pos_ventacero.script', function (require) {
    "use strict";

    var model = require('point_of_sale.models');
    var field_utils = require('web.field_utils');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    model.Orderline = model.Orderline.extend({    

        set_quantity: function(quantity, keep_price){
            this.order.assert_editable();
            if(quantity === 'remove'){
                if (this.refunded_orderline_id in this.pos.toRefundLines) {
                    delete this.pos.toRefundLines[this.refunded_orderline_id];
                }
                this.order.remove_orderline(this);
                return true;
            }else{
                var quant = typeof(quantity) === 'number' ? quantity : (field_utils.parse.float('' + quantity) || 0);
                if (this.refunded_orderline_id in this.pos.toRefundLines) {
                    const toRefundDetail = this.pos.toRefundLines[this.refunded_orderline_id];
                    const maxQtyToRefund = toRefundDetail.orderline.qty - toRefundDetail.orderline.refundedQty
                    if (quant > 0) {
                        Gui.showPopup('ErrorPopup', {
                            title: _t('Positive quantity not allowed'),
                            body: _t('Only a negative quantity is allowed for this refund line. Click on +/- to modify the quantity to be refunded.')
                        });
                        return false;
                    } else if (quant == 0) {
                        toRefundDetail.qty = 0;
                    } else if (-quant <= maxQtyToRefund) {
                        toRefundDetail.qty = -quant;
                    } else {
                        Gui.showPopup('ErrorPopup', {
                            title: _t('Greater than allowed'),
                            body: _.str.sprintf(
                                _t('The requested quantity to be refunded is higher than the refundable quantity of %s.'),
                                this.pos.formatProductQty(maxQtyToRefund)
                            ),
                        });
                        return false;
                    }
                }
                var unit = this.get_unit();
                    if(unit){
                        if (unit.rounding) {
                            var decimals = 2;
                            var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                            this.quantity    = round_pr(quant, rounding);
                            this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                        } else {
                            this.quantity    = round_pr(quant, 1);
                            this.quantityStr = this.quantity.toFixed(0);
                        }
                    }else{
                        this.quantity    = quant;
                        this.quantityStr = '' + this.quantity;
                    }
                }

            // just like in sale.order changing the quantity will recompute the unit price
            if (!keep_price && !this.price_manually_set && !(
                this.pos.config.product_configurator && _.some(this.product.attribute_line_ids, (id) => id in this.pos.attributes_by_ptal_id))){
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
                this.order.fix_tax_included_price(this);
            }
            this.trigger('change', this);
            return true;
        }
    
    });
   });