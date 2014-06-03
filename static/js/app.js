(function() {

    FastClick.attach(document.body);

    var B = Backbone;
    var M = B.Marionette;

    var User = B.Model.extend({

        idAttribute: '_id',

        log: function(amount) {
            return $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/user/' + this.getId() + '/deposit',
                data: {
                    amount: amount
                }
            });
        },

        getId: function() {
            return this.get('_id')['$oid'];
        }

    })

    var Exercise = B.Model.extend({

        idAttribute: 'eid',

        defaults: {
            eid: null,
            quantity: null,
            name: null,
            value: null
        },

        log: function(user) {
            user.log(this.get('eid'));
        },

        delete: function() {
            return $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/user/' + user.getId() + '/exercise/' + this.get('eid') + '/delete',
            });
        },

        save: function(data) {
            this.set(data);
            return $.ajax({
                type: 'post',
                dataType: 'json',
                url: '/user/' + user.getId() + '/exercises/edit',
                data: this.toJSON()
            });
        }

    });

    var Exercises = B.Collection.extend({
        model: Exercise
    });

    var Header = M.ItemView.extend({

        template: '#tpl-header',

        initialize: function() {
            this.listenTo(this.model, 'change:balance', this.updateBalance);
        },

        ui: {
            loadingBar: '.loading-bar'
        },

        startLoading: function() {
            this.ui.loadingBar
                .removeClass('loading-done')
                .addClass('loading-one');
        },

        finishLoading: function() {
            this.ui.loadingBar
                .removeClass('loading-one')
                .addClass('loading-done');
        },

        updateBalance: function() {
            this.render();
            this.$el.find('.balance').addClass('update');
        },
    });

    var ExerciseView = M.ItemView.extend({
        events: {
            'click .description': 'onClickEdit',
            'click .deposit': 'onClickDeposit'
        },

        tagName: 'div',

        className: 'exercise',

        template: '#tpl-exercise',

        onClickEdit: function() {
            App.commands.execute('show-modal', new CreateExerciseView({model: this.model}));
        },

        onClickDeposit: function() {
            var req = user.log(this.model.get('value'));
            req.done(function(response) {
                user.set(response);
            });
        }

    });

    var ExerciseList = M.CollectionView.extend({
        itemView: ExerciseView,
        initialize: function() {
            this.listenTo(this.collection, 'change', this.render);
        }
    });

    var Body = M.ItemView;

    var MainNav = M.ItemView.extend({

        events: {
            'click [data-panel-trigger]': 'showPanel'
        },

        ui: {
            activeIndicator: '.active-indicator'
        },

        initialize: function() {
            this.bindUIElements();
        },

        showPanel: function(e) {
            var panel = $(e.currentTarget).data('panel-trigger');
            App.commands.execute('show-panel', panel);
        },

        activateTab: function(index) {
            var triggers = this.$el.find('[data-panel-trigger]');

            $(triggers.removeClass('active').get(index))
                .addClass('active');
            
            // TODO: make more generic
            var leftPos = index * 50 + '%'
            this.ui.activeIndicator.css({ left: leftPos });
        },

    });

    var StatsPanel = M.Layout.extend({
        template: '#tpl-stats-panel',
    });

    var QuickLogView = M.ItemView.extend({
        template: '#tpl-quick-log-form',

        events: {
            'click [data-quick-log]': 'onQuickLog'
        },

        ui: {
            value: '[name="value"]'
        },

        onQuickLog: function(e) {
            e.preventDefault();

            var data = {
                amount: this.ui.value.val()
            }

            var req = $.ajax({
                url: '/user/' + user.getId() + '/deposit',
                type: 'post',
                dataType: 'json',
                data: data
            });

            req.done(function(response) {
                user.set({balance: response.balance});
                App.commands.execute('close-modal');
            });

        },
    });
    var CreateExerciseView = M.ItemView.extend({

        ui: {
            quantity: '[name="quantity"]',
            name: '[name="name"]',
            value: '[name="value"]'
        },

        events: {
            'click [data-delete-exercise]': 'onDeleteExercise',
            'click [data-save-exercise]': 'onSaveExercise',
        },

        template: '#tpl-create-exercise-form',

        onDeleteExercise: function(e) {
            e.preventDefault();
            var req = this.model.delete();
            req.done(function(response) {
                exercises.set(response.exercises);
                App.commands.execute('close-modal');
            });
        },

        onSaveExercise: function(e) {
            e.preventDefault();

            var data = {
                quantity: this.ui.quantity.val(),
                name: this.ui.name.val(),
                value: this.ui.value.val(),
            };

            var req = this.model.save(data);
            req.done(function(response) {
                user.set(response);
                exercises.set(response.exercises);
                App.commands.execute('close-modal');
            });
        }

    });

    var ExercisePanel = M.Layout.extend({

        events: {
            'click [data-trigger="quick-log"]': 'onTriggerQuickLog',
            'click [data-trigger="create-exercise"]': 'onTriggerCreateExercise',
        },

        onTriggerQuickLog: function() {
            App.commands.execute('show-modal', new QuickLogView());
        },

        onTriggerCreateExercise: function() {
            App.commands.execute('show-modal', new CreateExerciseView({model: new Exercise()}));
        },

        regions: {
            Exercises: '.exercises',
        },

        template: '#tpl-exercise-panel',

        onShow: function() {
            this.Exercises.show(new ExerciseList({collection: exercises}));
        }

    });

    var PanelLayout = M.Layout.extend({

        events: {
            'touchstart'          : 'handleTouchStart',
            'touchmove'           : 'handleTouchMove',
            'touchend'            : 'handleTouchEnd',
            'touchcancel'         : 'handleTouchEnd',
            'webkitTransitionEnd' : 'handleTransitionEnd',
        },

        ui: {
            panelWrapper: '.panel-wrapper'
        },

        regions: {
            PanelWrapper: '.panel-wrapper',
            ExercisePanel: '.exercise-panel',
            StatsPanel: '.stats-panel',
        },

        initialize: function() {
            this.index = 0;

            this.bindUIElements();
            this.ExercisePanel.show(new ExercisePanel),
            this.StatsPanel.show(new StatsPanel({model: user}))
            this.layout();
        },

        layout: function() {
            this.x = 0;
            this.width = this.$el.width();
            this.offset = this.$el.offset();
            this.ExercisePanel.$el.css({width: this.width});
            this.StatsPanel.$el.css({width: this.width});
            this.ui.panelWrapper.css({width: this.width * 2});
        },

        translateStr: function(deltax) {
            return 'translate3d(' + deltax + 'px, 0, 0)';
        },

        sub: function(a, b) {
            var
                ax = a.x || a.clientX || a.left,
                bx = b.x || b.clientX || b.left,
                ay = a.y || a.clientY || a.top,
                by = b.y || b.clientY || b.top;

            return { x: ax - bx, y: ay - by};
        },

        handleTransitionEnd: function() {
            this.transitionOff();
        },

        handleTouchStart: function(e) {
            var touch = e.originalEvent.targetTouches[0];
            this.startCoords = this.sub(touch, this.offset)
            this.lastCoords = this.startCoords;
        },

        handleTouchMove: function(e) {

            var touch = e.originalEvent.changedTouches[0];
            var touchOffset = this.sub(touch, this.offset)
            var totalDiff = this.sub(this.startCoords, touchOffset);

            if (Math.abs(totalDiff.x) < 10) {
                return;
            }

            var diff = this.sub(touchOffset, this.lastCoords);

            if (diff.x < 0) {

                if (this.hasNext()) {
                    this.translate(diff.x);
                } else {
                    return;
                }

            } else {

                if (this.hasPrev()) {
                    this.translate(diff.x);
                } else {
                    return;
                }
            }

            this.lastCoords = this.sub(touch, this.offset);
        },

        handleTouchEnd: function(e) {

            var touch = e.originalEvent.changedTouches[0];
            var diff = this.sub(this.startCoords, this.lastCoords);

            if (Math.abs(diff.x) > this.width / 4) {
                diff.x > 0 ? this.next() : this.prev();
            } else {
                this.snap(this.sub(this.startCoords, this.lastCoords).x);
            }
        },

        hasNext: function() {
            // TODO pass this in somehow when you extract to behavoir
            return this.index < 1;
        },

        hasPrev: function() {
            return this.index > 0;
        },

        next: function() {
            this.index = this.index + 1;
            this.transitionOn();
            this.moveTo(this.index);
        },

        prev: function() {
            this.index = this.index - 1;
            this.transitionOn();
            this.moveTo(this.index);
        },

        moveTo: function(index) {
            App.vent.trigger('panel:change', index, this.ui.panelWrapper.children().get(index));
            this.translateTo(-(index * this.width));
        },

        moveToByClass: function(className) {
            this.transitionOn();
            var index = this.$el.find("." + className).index();
            this.moveTo(index);
        },

        translate: function(deltax) {
            this.x = this.x + deltax;
            this.setWrapperCss({'webkitTransform': this.translateStr(this.x)});
        },

        snap: function(deltax) {
            this.transitionOn();
            this.translate(deltax);
        },

        transitionOn: function() {
            this.setTransition('-webkit-transform .3s');
        }, 

        transitionOff: function() {
            this.setTransition('');
        }, 

        setTransition: function(transition) {
            this.setWrapperCss({'webkitTransition': transition});
        },

        translateTo: function(x) {
            this.x = x;
            this.setWrapperCss({'webkitTransform': this.translateStr(this.x)})
        },

        setWrapperCss: function(css) {
            this.ui.panelWrapper.css(css);
        },

    })

    var ModalLayout = M.Layout.extend({

        events: {
            'click .close': 'onClickClose'
        },

        regions: {
            CloseBtn: '.close',
            Body: '.modal-body'
        },

        initialize: function() {
            this.bindUIElements();
        },

        show: function(view) {
            this.Body.show(view);
            this.$el.addClass('active');
        },

        close: function() {
            this.$el.removeClass('active');
        },

        onClickClose: function() {
            App.commands.execute('close-modal');
        },

    });

    var Controller = M.Controller.extend({

        showPanel: function(panel) {
            panelLayout.moveToByClass(panel);
        },

        showModal: function(view) {
           modal.show(view);
           App.Body.$el.addClass('receding');
        },

        closeModal: function() {
           modal.close();
           App.Body.$el.removeClass('receding');
        },

        updateNav: function(index) {
            mainNav.activateTab(index);
        },

    });

    window.App = new M.Application;
    window.user = new User(Context);
    window.exercises = new Exercises(Context.exercises);
    var header = new Header({model: user});
    var body = new Body({el: $('#body')});
    var panelLayout = new PanelLayout({el: '.panels'});
    var mainNav = new MainNav({el: $('.main-nav')});
    var modal = new ModalLayout({el: $('#modal')});

    App.addRegions({
        Frame: '#frame',
        Body: '#body',
        Header: 'header',
        ExercisePanel: '.exercise-panel',
        MainNav: '.main-nav',
        Panels: '.panels',
        Modal: '#modal',
    });

    App.addInitializer(function(options) {

        var controller = new Controller();
        App.commands.setHandler('show-panel', controller.showPanel, controller);
        App.commands.setHandler('show-modal', controller.showModal, controller);
        App.commands.setHandler('close-modal', controller.closeModal, controller);
        App.vent.on('panel:change', controller.updateNav, controller);

        App.Frame.ensureEl();
        App.Body.ensureEl();

        App.Header.show(header);
        App.Body.attachView(body);
        App.Panels.attachView(panelLayout);
        App.MainNav.attachView(mainNav);
        App.Modal.attachView(modal);

        $(document).ajaxStart(_.bind(header.startLoading, header));
        $(document).ajaxComplete(_.bind(header.finishLoading, header));
        $(document).ajaxError(_.bind(header.finishLoading, header));

    });

    App.start();

})()
