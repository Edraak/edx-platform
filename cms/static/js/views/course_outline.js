define(["jquery", "underscore", "gettext", "js/views/xblock_outline", "js/views/utils/view_utils",
        "js/views/utils/xblock_utils"],
    function($, _, gettext, XBlockOutlineView, ViewUtils, XBlockViewUtils) {

        var CourseOutlineView = XBlockOutlineView.extend({
            // takes XBlockInfo as a model

            initialize: function() {
                XBlockOutlineView.prototype.initialize.call(this);
            },

            shouldExpandChildren: function() {
                // Expand the children if this xblock's locator is in the intially expanded state
                if (this.initialState && _.indexOf(this.initialState.expandedLocators, this.model.id) >= 0) {
                    return true;
                }
                // Only expand sections initially
                var category = this.model.get('category');
                return this.renderedChildren || category === 'course' || category === 'chapter';
            },

            shouldRenderChildren: function() {
                // Render all nodes up to verticals but not below
                return this.model.get('category') !== 'vertical';
            },

            createChildView: function(xblockInfo, parentInfo) {
                return new CourseOutlineView({
                    model: xblockInfo,
                    parentInfo: parentInfo,
                    template: this.template,
                    parentView: this
                });
            },

            getExpandedLocators: function() {
                var expandedLocators = [];
                this.$('.outline-item.is-collapsible').each(function(index, rawElement) {
                    var element = $(rawElement);
                    if (!element.hasClass('collapsed')) {
                        expandedLocators.push(element.data('locator'));
                    }
                });
                return expandedLocators;
            },

            /**
             * Refresh the containing section (if there is one) or else refresh the entire course.
             * Note that the refresh will preserve the expanded state of this view and all of its
             * children.
             * @param viewState The desired initial state of the view, or null if none.
             * @returns {*} A promise representing the refresh operation.
             */
            refresh: function(viewState) {
                var getViewToRefresh = function(view) {
                        if (view.model.get('category') === 'chapter' || !view.parentView) {
                            return view;
                        }
                        return getViewToRefresh(view.parentView);
                    },
                    view = getViewToRefresh(this),
                    expandedLocators = view.getExpandedLocators();
                viewState = viewState || {};
                viewState.expandedLocators = expandedLocators.concat(viewState.expandedLocators || []);
                view.initialState = viewState;
                return view.model.fetch({});
            },

            handleAddEvent: function(event) {
                var self = this,
                    target = $(event.target),
                    category = target.data('category');
                event.preventDefault();
                XBlockViewUtils.addXBlock(target).done(function(locator) {
                    self.onChildAdded(locator, category);
                });
            },

            onChildAdded: function(locator, category) {
                // For units, redirect to the new page, and for everything else just refresh inline.
                if (category === 'vertical') {
                    ViewUtils.redirect('/container/' + locator);
                } else {
                    // Refresh the view, and show the new block expanded and with its name editable
                    this.refresh({
                        editDisplayName: locator,
                        expandedLocators: [ locator ]
                    });
                }
            },

            onChildDeleted: function() {
                this.refresh();
            },

            addButtonActions: function(element) {
                XBlockOutlineView.prototype.addButtonActions.call(this, element);
                element.find('.add-button').click(_.bind(this.handleAddEvent, this));
            }
        });

        return CourseOutlineView;
    }); // end define();
