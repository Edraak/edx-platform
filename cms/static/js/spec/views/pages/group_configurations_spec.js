define([
    'jquery', 'underscore', 'js/views/pages/group_configurations',
    'js/collections/group_configuration'
], function ($, _, GroupConfigurationsPage, GroupConfigurationCollection) {
    'use strict';
    describe('GroupConfigurationsPage', function() {
        var mockGroupConfigurationsPage = readFixtures(
                'mock/mock-group-configuration-page.underscore'
            ),
            noGroupConfigurationsTpl = readFixtures(
                'no-group-configurations.underscore'
            ), view;

        beforeEach(function () {
            setFixtures($('<script>', {
                id: 'no-group-configurations-tpl',
                type: 'text/template'
            }).text(noGroupConfigurationsTpl));
            appendSetFixtures(mockGroupConfigurationsPage);

            view = new GroupConfigurationsPage({
                el: $('.content-primary'),
                collection: new GroupConfigurationCollection()
            });
        });

        describe('Initial display', function() {
            it('can render itself', function() {
                expect(view.$('.ui-loading')).toBeVisible();
                view.render();
                expect(view.$('.no-group-configurations-content')).toBeTruthy();
                expect(view.$('.ui-loading')).toBeHidden();
            });
        });
    });
});
