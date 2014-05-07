(function() {

    window.Overlay = function(options) {

        this.mask = $(options.mask);

        this.header = this.mask.find('header');
        this.content = this.mask.find('section');
        this.footer = this.mask.find('footer');

        this.headerTpl = _.template(options.headerTpl || '');
        this.contentTpl = _.template(options.contentTpl || '');
        this.footerTpl = _.template(options.footerTpl || '');

        this.initEvents();

    }

    window.Overlay.prototype = {

        initEvents: function() {
            this.mask.on('click', _.bind(this.close, this));
            this.mask.on('transitionend webkitTransitionEnd oTransitionEnd otransitionend MSTransitionEnd', _.bind(this.cleanUp, this));
        },

        stop: function(e) {
            e.stopPropagation;
        },

        setHeader: function(html) {
            this.header.html(html);
        },

        setContent: function(html) {
            this.content.html(html);
        },

        setFooter: function(html) {
            this.content.html(html);
        },

        renderHeader: function(data) {
            this.setHeader(this.headerTpl(data));
        },

        renderContent: function(data) {
            this.setContent(this.contentTpl(data));
        },

        renderFooter: function(data) {
            this.setFooter(this.footerTpl(data));
        },

        render: function(data) {
            this.renderHeader(data.headerData);
            this.renderContent(data.contentData);
            this.renderFooter(data.footerData);
        },

        open: function() {
            this.isOpen = true;
            this.mask.show();
            this.triggerReflow();
            this.mask.addClass('show');
            this.mask.trigger('show:overlay', this);
        },

        close: function(e) {
            if (e.target == this.mask.get(0)) {
                this.isOpen = false;
                this.mask.removeClass('show');
                this.mask.trigger('close:overlay', this);
            }
        },

        triggerReflow: function() {
            this.mask.css('background');
        },

        cleanUp: function() {
            if (!this.isOpen) {
                this.mask.hide();
            }
        }

    }


})()

