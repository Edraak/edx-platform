define(["jquery", "underscore", "js/views/baseview"], function($, _, BaseView) {
    var Outline = BaseView.extend({
        events : {
        },

        initialize: function() {
            this.expandButtonTemplate = _.template($("#expand-button-tpl").text());
        },

        render: function() {
            var root = this.root,
                articleElement,
                html = this.getHtml(root);
            this.$el.html(html);
            return this;
        },

        getHtml: function(xblock) {
            var html = '',
                xblocks = xblock.get('children'),
                category = xblock.get('category'),
                childCategory = this.getChildCategory(category),
                childListClass = this.getListClass(childCategory);
            html += '<div class="form-content">';
            html += this.getListHtml(xblocks, childListClass);
            html += '</div>';
            return html;
        },

        getListHtml: function(xblocks, listClass) {
            var html = '',
                childXBlock,
                childHtml = '';
            for (var i=0; i < xblocks.length; i++) {
                childXBlock = xblocks[i];
                childHtml += this.getItemHtml(childXBlock);
            }
            if (childHtml) {
                html += '<ol class="' + listClass + '">';
                html += childHtml;
                html += '</ol>\n';
            }
            return html;
        },

        getChildCategory: function(category) {
            if (category === 'course') {
                return 'chapter';
            } else if (category === 'chapter') {
                return 'sequential';
            } else if (category === 'sequential') {
                return 'vertical';
            } else {
                return 'component';
            }
        },

        getListClass: function(category) {
            if (category === 'chapter') {
                return 'section-list';
            } else if (category === 'sequential') {
                return 'subsection-list';
            } else if (category === 'vertical') {
                return 'unit-list';
            } else {
                return 'component-list';
            }
        },

        getItemHtml: function(xblock) {
            var html = '',
                displayName = xblock.display_name,
                category = xblock.category,
                itemClass = this.getListClass(category) + '-item',
                itemLabelClass = itemClass + '-label',
                childCategory = this.getChildCategory(category),
                childListClass = this.getListClass(childCategory),
                isCollapsible = xblock.children && xblock.children.length > 0,
                childListHtml = '';
            if (this.shouldShowItem(xblock)) {
                if (isCollapsible) {
                    childListHtml = this.getListHtml(xblock.children, childListClass);
                    isCollapsible = childListHtml !== '';
                }
                html += '<li class="' + itemClass;
                if (isCollapsible) {
                    html += ' is-collapsible"';
                }
                html += '">';
                html += '<div class="' + itemLabelClass + '">\n';
                if (isCollapsible) {
                    html += this.expandButtonTemplate() + '\n';
                }
                html += '<span>' + displayName + '</span>\n';
                html += '</div\n>';
                if (childListHtml) {
                    html += childListHtml;
                }
                html += '</li>\n';
            }
            return html;
        },

        shouldShowItem: function(xblock) {
            var category = xblock.category;
            return category === 'chapter' ||
                category === 'sequential' ||
                category === 'vertical';
        }
    });

    return Outline;
});
