openerp_announcement = function(instance) {
    instance.web.WebClient.include({
        show_application: function() {
            return $.when(this._super.apply(this, arguments));
        },
        show_annoucement_bar: function() {
        }
    });
};
