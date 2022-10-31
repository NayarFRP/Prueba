/** @odoo-module alias=stock_ventacero.counted_quantity_uom_p_widget **/

import BasicFields from 'web.basic_fields';
import fieldRegistry from 'web.field_registry';

const CountedQuantityUomPWidgetField = BasicFields.FieldFloat.extend({
    supportedFieldTypes: ['float'],

     _renderReadonly: function () {
        if (this.recordData.inventory_quantity_set) {
            this.el.textContent = this._formatValue(this.recordData.inventory_quantity_uom_p);
        } else {
            this.el.textContent = "";
        }
    },

    _isSameValue: function(value) {
        // We want to trigger the update of the view when inserting 0
        if (value == 0) {
            return false;
        }
        return this._super(...arguments);
    }

});

fieldRegistry.add('counted_quantity_uom_p_widget', CountedQuantityUomPWidgetField);

export default CountedQuantityUomPWidgetField;