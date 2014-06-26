define(["jquery", "underscore", "gettext", "js/views/baseview", "js/views/utils/xblock_utils",
        "js/views/xblock_string_field_editor"],
    function($, _, gettext, BaseView, XBlockViewUtils, XBlockStringFieldEditor) {

        var XBlockOutlineView = BaseView.extend({
            // takes XBlockInfo as a model

            initialize: function() {
                BaseView.prototype.initialize.call(this);
                this.template = this.options.template;
                if (!this.template) {
                    this.template = this.loadTemplate('xblock-outline');
                }
                this.parentInfo = this.options.parentInfo;
                this.parentView = this.options.parentView;
                this.renderedChildren = false;
                this.model.on('change', this.onXBlockChange, this);
            },

            render: function() {
                this.renderTemplate();
                this.addButtonActions(this.$el);
                this.nameEditor = new XBlockStringFieldEditor({
                    el: this.$('.wrapper-xblock-field'),
                    model: this.model
                });
                this.nameEditor.render();
                if (this.shouldRenderChildren() && this.shouldExpandChildren()) {
                    this.renderChildren();
                }
                if (this.initialState && this.model.id === this.initialState.editDisplayName) {
                    this.nameEditor.$('.xblock-field-value').click();
                }
                this.initialState = null;
                return this;
            },

            renderChildren: function() {
                var i, children, listElement, childOutlineView;
                listElement = this.$('.sortable-list');
                children = this.model.get('children');
                for (i=0; i < children.length; i++) {
                    childOutlineView = this.createChildView(children[i], this.model);
                    childOutlineView.initialState = this.initialState;
                    childOutlineView.render();
                    listElement.append(childOutlineView.$el);
                }
                this.renderedChildren = true;
            },

            toggleExpandCollapse: function(event) {
                // Ensure that the children have been rendered before expanding
                if (this.shouldRenderChildren() && !this.renderedChildren) {
                    this.renderChildren();
                }
                BaseView.prototype.toggleExpandCollapse.call(this, event);
            },

            addButtonActions: function(element) {
                var self = this;
                element.find('.configure-button').click(function(event) {
                    event.preventDefault();
                    self.editXBlock($(event.target));
                });
                element.find('.delete-button').click(function(event) {
                    event.preventDefault();
                    self.deleteXBlock($(event.target));
                });
            },

            shouldRenderChildren: function() {
                return true;
            },

            shouldExpandChildren: function() {
                return true;
            },

            createChildView: function(xblockInfo, parentInfo) {
                return new XBlockOutlineView({
                    model: xblockInfo,
                    parentInfo: parentInfo,
                    template: this.template,
                    parentView: this
                });
            },

            renderTemplate: function() {
                var xblockInfo = this.model,
                    childInfo = xblockInfo.get('child_info'),
                    parentInfo = this.parentInfo,
                    xblockType = this.getXBlockType(this.model.get('category'), this.parentInfo),
                    parentType = parentInfo ? this.getXBlockType(parentInfo.get('category')) : null,
                    addChildName = null,
                    defaultNewChildName = null,
                    html,
                    isCollapsed = this.shouldRenderChildren() && !this.shouldExpandChildren();
                if (childInfo) {
                    addChildName = interpolate(gettext('Add %(component_type)s'), {
                        component_type: childInfo.display_name
                    }, true);
                    defaultNewChildName = interpolate(gettext('New %(component_type)s'), {
                        component_type: childInfo.display_name
                    }, true);
                }
                html = this.template({
                    xblockInfo: xblockInfo,
                    parentInfo: this.parentInfo,
                    xblockType: xblockType,
                    parentType: parentType,
                    childType: childInfo ? this.getXBlockType(childInfo.category, xblockInfo) : null,
                    childCategory: childInfo ? childInfo.category : null,
                    addChildLabel: addChildName,
                    defaultNewChildName: defaultNewChildName,
                    isCollapsed: isCollapsed,
                    includesChildren: this.shouldRenderChildren()
                });
                if (this.parentInfo) {
                    this.setElement($(html));
                } else {
                    this.$el.html(html);
                }
            },

            getXBlockType: function(category, parentInfo) {
                var xblockType = category;
                if (category === 'chapter') {
                    xblockType = 'section';
                } else if (category === 'sequential') {
                    xblockType = 'subsection';
                } else if (category === 'vertical' && parentInfo && parentInfo.get('category') === 'sequential') {
                    xblockType = 'unit';
                }
                return xblockType;
            },

            onXBlockChange: function() {
                var oldElement = this.$el;
                this.render();
                if (this.parentInfo) {
                    oldElement.replaceWith(this.$el);
                }
                // If there is a non-hidden XBlock field input then give it the focus
                this.$('.xblock-field-input:visible').first().each(function (index, element) {
                    $(element).focus();
                });
            },

            onChildDeleted: function() {
                // Update the model so that we get the latest publish and last modified information.
                this.model.fetch();
            },

            deleteXBlock: function() {
                var parentView = this.parentView;
                XBlockViewUtils.deleteXBlock(this.model).done(function() {
                    if (parentView) {
                        parentView.onChildDeleted();
                    }
                });
            }
        });

        return XBlockOutlineView;
    }); // end define();
