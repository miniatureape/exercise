(function() {

    function getTemplate(id) {
        return _.template($(id).html())
    }

    var ExerciseEditor = function(options) {
        this.overlay = options.overlay;
        this.bus = options.bus;
        this.editBtns = options.editBtns;
        this.addBtn = options.addBtn;

        this.contentTpl = getTemplate('#overlay-content-tpl');
        this.editHeaderTpl = getTemplate('#edit-overlay-header-tpl');
        this.editFooterTpl = getTemplate('#edit-overlay-footer-tpl');

        this.createHeaderTpl = getTemplate('#create-overlay-header-tpl');
        this.createFooterTpl = getTemplate('#create-overlay-footer-tpl');

        this.newFormData = {
            eid: null,
            name: null,
            quantity: null,
            value: null
        };
        this.initEvents();
    }

    _.extend(ExerciseEditor.prototype, {

        initEvents: function() {
            this.overlay.mask.on('click', '.save', _.bind(this.saveExercise, this));
            this.editBtns.on('click', _.bind(this.openEditOverlay, this));
            this.addBtn.on('click', _.bind(this.openCreateOverlay, this));
        },

        saveExercise: function() {
            var form = this.overlay.mask.find('.edit-form');
            form.submit();
        },

        openEditOverlay: function(e) {
            var data = $(e.currentTarget).data();
            this.overlay.setHeader(this.editHeaderTpl(data));
            this.overlay.setContent(this.contentTpl(data));
            this.overlay.setFooter(this.editFooterTpl(data));
            this.overlay.open();
        },

        openCreateOverlay: function() {
            var data = this.newFormData;
            overlay.setHeader(this.createHeaderTpl(data));
            overlay.setContent(this.contentTpl(data));
            overlay.setFooter(this.createFooterTpl(data));
            overlay.open();
        }

    });

    var overlay = new Overlay({mask: '#overlay'});
    var quickLogOverlay = new Overlay({mask: '#ql-overlay'});


    var editor = new ExerciseEditor({
        overlay: overlay,
        editBtns: $('.edit-exercise'),
        addBtn: $('.add-btn'),
        bus: $('#bus'),
    });

    var quickLog = $('.quick-log');

    quickLog.on('click', function(e) {
        quickLogOverlay.open();
    });

    function DepositForm(form, bus) { 
        this.form = $(form); 
        this.button = this.form.find('button'); 
        this.bus = $(bus); this.initEvents(); 
    } 

    DepositForm.prototype = { 

        initEvents: function() { 
            this.form.on('submit', $.proxy(this.onSubmit, this)); 
        }, 

        onSubmit: function(e) { 
            e.preventDefault(); 
            this.displayWait(); 
            this.postRequest();
        }, 

        postRequest: _.throttle(function() {
            var req = $.ajax({ 
                type: 'post', 
                dataType: 'json', 
                url: this.form.attr('action'), 
                data: this.form.serialize() 
            }); 
            req.done($.proxy(this.onDone, this)); 
            req.fail($.proxy(this.onFail, this)); 
        }, 300),

        displayWait: function() { 
             this.button.addClass('waiting'); 
        }, 

        displayReady: function() { 
             this.button.removeClass('waiting'); 
        }, 

        onDone: function(result) {
            var newBalance = result.balance;
            // TODO make this a  little more robust
            this.bus.trigger('new-balance', newBalance);
            this.displayReady();
        },

        onFail: function(e) {
            this.displayReady();
        }

    }

    $('.deposit-form').each(function(index, elem) {
        new DepositForm(elem, document.body);
    });

    $(document.body).on('new-balance', function(e, balance) {
        $('.icon-chart-bar').removeClass('positive negative').addClass(balance >= 0 ? 'positive' : 'negative');
        $('.balance-amount').html(balance);
        quickLogOverlay.close();
    });


})()
