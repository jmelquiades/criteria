odoo.define('l10n_pe_ruc.datepicker', function (require) {
"use strict";
var widget_datapicker = require('web.datepicker');

var DateWidget = widget_datapicker.DateWidget;
DateWidget.include({
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.options['minDate'] = moment({ y: 1800 });
    },
});

});
