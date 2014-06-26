define([
    'js/models/group_configuration', 'js/models/course',
    'js/collections/group_configuration',
    'js/views/group_configuration_details',
    'js/views/group_configurations_list', 'js/views/group_configuration_edit',
    'js/views/group_configuration_item', 'js/models/group',
    'js/collections/group', 'js/views/group_edit',
    'js/views/feedback_notification',
    'js/spec_helpers/create_sinon', 'jasmine-stealth'
], function(
    GroupConfigurationModel, Course, GroupConfigurationSet,
    GroupConfigurationDetails, GroupConfigurationsList, GroupConfigurationEdit,
    GroupConfigurationItem, GroupModel, GroupSet, GroupEdit, Notification,
    create_sinon
) {
    'use strict';
    beforeEach(function() {
        window.course = new Course({
            id: '5',
            name: 'Course Name',
            url_name: 'course_name',
            org: 'course_org',
            num: 'course_num',
            revision: 'course_rev'
        });

        this.addMatchers({
            toContainText: function(text) {
                var trimmedText = $.trim(this.actual.text());

                if (text && $.isFunction(text.test)) {
                    return text.test(trimmedText);
                } else {
                    return trimmedText.indexOf(text) !== -1;
                }
            }
        });
    });

    afterEach(function() {
        delete window.course;
    });

    describe('GroupConfigurationDetails', function() {
        var tpl = readFixtures('group-configuration-details.underscore');

        beforeEach(function() {
            setFixtures($('<script>', {
                id: 'group-configuration-details-tpl',
                type: 'text/template'
            }).text(tpl));

            this.model = new GroupConfigurationModel({
                name: 'Configuration',
                description: 'Configuration Description',
                id: 0
            });

            spyOn(this.model, 'destroy').andCallThrough();
            this.collection = new GroupConfigurationSet([ this.model ]);
            this.view = new GroupConfigurationDetails({
                model: this.model
            });
        });

        describe('Basic', function() {
            it('should render properly', function() {
                this.view.render();

                expect(this.view.$el).toContainText('Configuration');
                expect(this.view.$el).toContainText('ID: 0');
            });

            it('should show groups appropriately', function() {
                this.model.get('groups').add([{}, {}, {}]);
                this.model.set('showGroups', false);
                this.view.render().$('.show-groups').click();

                expect(this.model.get('showGroups')).toBeTruthy();
                expect(this.view.$('.group').length).toBe(3);
                expect(this.view.$('.group-configuration-groups-count'))
                    .not.toExist();
                expect(this.view.$('.group-configuration-description'))
                    .toContainText('Configuration Description');
                expect(this.view.$('.group-allocation'))
                    .toContainText('33%');
            });

            it('should hide groups appropriately', function() {
                this.model.get('groups').add([{}, {}, {}]);
                this.model.set('showGroups', true);
                this.view.render().$('.hide-groups').click();

                expect(this.model.get('showGroups')).toBeFalsy();
                expect(this.view.$('.group').length).toBe(0);
                expect(this.view.$('.group-configuration-groups-count'))
                    .toContainText('Contains 3 groups');
                expect(this.view.$('.group-configuration-description'))
                    .not.toExist();
                expect(this.view.$('.group-allocation'))
                    .not.toExist();
            });
        });
    });

    describe('GroupConfigurationEdit', function() {
        var groupTpl = readFixtures('group-edit.underscore'),
            tpl = readFixtures('group-configuration-edit.underscore');

        beforeEach(function() {
            setFixtures($('<script>', {
                id: 'group-configuration-edit-tpl',
                type: 'text/template'
            }).text(tpl));

            appendSetFixtures($('<script>', {
                id: 'group-edit-tpl',
                type: 'text/template'
            }).text(groupTpl));

            appendSetFixtures(sandbox({
                id: 'page-notification'
            }));

            this.model = new GroupConfigurationModel({
                name: 'Configuration',
                description: 'Configuration Description',
                id: 0,
                editing: true
            });
            this.collection = new GroupConfigurationSet([this.model], {
                url: '/group_configurations'
            });
            this.view = new GroupConfigurationEdit({
                model: this.model
            });
            spyOn(this.view, 'render').andCallThrough();
        });

        describe('Basic', function() {
            beforeEach(function () {
                spyOn(this.model, 'save');
            });

            it('should render properly', function() {
                this.view.render();
                expect(this.view.$('.group-configuration-name-input').val())
                    .toBe('Configuration');
                expect(
                    this.view.$('.group-configuration-description-input').val()
                ).toBe('Configuration Description');
            });

            it('should save properly', function() {
                this.view.render();
                this.view.$('.group-configuration-name-input').val(
                    'New Configuration'
                );
                this.view.$('.group-configuration-description-input').val(
                    'New Description'
                );
                this.view.$('form').submit();

                expect(this.model.get('name')).toBe('New Configuration');
                expect(this.model.get('description')).toBe('New Description');

                expect(this.model.save).toHaveBeenCalled();
            });

            it('should not save on invalid', function() {
                this.view.render();
                this.view.$('.group-configuration-name-input').val('');
                this.view.$('form').submit();
                expect(this.model.validationError).toBeTruthy();
                expect(this.model.save).not.toHaveBeenCalled();
            });

            it('does not save on cancel', function() {
                this.view.render();
                this.view.$('.group-configuration-name-input').val(
                    'New Configuration'
                );
                this.view.$('.group-configuration-description-input').val(
                    'New Description'
                );
                this.view.$('.action-cancel').click();
                expect(this.model.get('name')).toBe('Configuration');
                expect(this.model.get('description')).toBe(
                    'Configuration Description'
                );
                expect(this.model.save).not.toHaveBeenCalled();
            });

            it('should be removed if it is a new item', function() {
                this.model.unset('id');
                this.view.render();
                this.view.$('.group-configuration-name-input').val(
                    'New Configuration'
                );
                this.view.$('.group-configuration-description-input').val(
                    'New Description'
                );
                this.view.$('.action-cancel').click();
                expect($('.group-configuration').length).toBe(0);
                expect(this.model.save).not.toHaveBeenCalled();
            });

            it('should be possible to correct validation errors', function() {
                this.view.render();
                this.view.$('.group-configuration-name-input').val('');
                this.view.$('form').submit();
                expect(this.model.validationError).toBeTruthy();
                expect(this.model.save).not.toHaveBeenCalled();
                this.view.$('.group-configuration-name-input').val(
                    'New Configuration'
                );
                this.view.$('form').submit();
                expect(this.model.validationError).toBeFalsy();
                expect(this.model.save).toHaveBeenCalled();
            });

            var message = 'should have appropriate class names on focus/blur';
            it(message, function () {
                this.view.render();
                var element = this.view.$('.group-configuration-name-input'),
                    parent = this.view.$('.add-group-configuration-name');

                element.focus();
                expect(parent).toHaveClass('is-focused');
                element.blur();
                expect(parent).not.toHaveClass('is-focused');

            var message = 'removes all empty groups on cancel if the model ' +
                        'has a non-empty group';
            it(message, function() {
                var groups = this.model.get('groups');

                groups.at(0).set('name', 'non-empty');
                this.model.setOriginalAttributes();
                this.view.render();
                groups.add([{}, {}, {}]);
                expect(groups.length).toEqual(5);
                this.view.$('.action-cancel').click();
                expect(groups.length).toEqual(2);
                expect(groups.first().get('name')).toEqual('non-empty');
            });

            message = 'removes all empty groups on cancel except two if the ' +
                    'model has no non-empty groups';
            it(message, function() {
                var groups = this.model.get('groups');
                this.view.render();
                groups.add([{}, {}, {}]);
                expect(groups.length).toEqual(5);
                this.view.$('.action-cancel').click();
                expect(groups.length).toEqual(2);
            });
        });

        describe('AJAX', function() {
            beforeEach(function() {
                this.savingSpies = spyOnConstructor(Notification, 'Mini', [
                    'show', 'hide'
                ]);
                this.savingSpies.show.andReturn(this.savingSpies);
            });

            it('should save itself and close editing view', function() {
                var requests = create_sinon.requests(this),
                    savingOptions;

                this.model.set('name', 'New Configuration Name');
                this.view.render().$('form').submit();

                // Saving massage should be shown
                expect(this.savingSpies.constructor).toHaveBeenCalled();
                expect(this.savingSpies.show).toHaveBeenCalled();
                expect(this.savingSpies.hide).not.toHaveBeenCalled();
                savingOptions = this.savingSpies.constructor.mostRecentCall
                                                                    .args[0];
                expect(savingOptions.title).toMatch(/Saving/);
                requests[0].respond(200);
                expect(this.savingSpies.hide).toHaveBeenCalled();
                // Close edit form on success save
                expect($('.edit-group-configuration').length).toBe(0);
                expect(this.model.get('editing')).toBeFalsy();
                expect(this.model.get('name')).toBe('New Configuration Name');
            });
        });
    });

    describe('GroupConfigurationsList', function() {
        var noGroupConfigurationsTpl = readFixtures(
            'no-group-configurations.underscore'
        );

        beforeEach(function() {
            var showEl = $('<li>');

            setFixtures($('<script>', {
                id: 'no-group-configurations-tpl',
                type: 'text/template'
            }).text(noGroupConfigurationsTpl));

            this.collection = new GroupConfigurationSet();
            this.view = new GroupConfigurationsList({
                collection: this.collection
            });
            this.view.render();
        });

        var message = 'should render the empty template if there are no ' +
                      'group configurations';
        it(message, function() {
            expect(this.view.$el).toContainText(
                'You haven\'t created any group configurations yet.'
            );
            expect(this.view.$el).toContain('.new-button');
            expect(
                this.view.$('.group-configurations-list-item').length
            ).toBe(0);
        });

        message = 'the empty template should disappear when new ' +
                      'group configuration is added';
        it(message, function() {
            var emptyMessage = 'You haven\'t created any group ' +
                'configurations yet.';

            expect(this.view.$el).toContainText(emptyMessage);
            expect(
                this.view.$('.group-configurations-list-item').length
            ).toBe(0);
            this.collection.add([{}]);
            expect(this.view.$el).not.toContainText(emptyMessage);
            expect(
                this.view.$('.group-configurations-list-item').length
            ).toBe(1);
        });

        message = 'should render GroupConfigurationDetails views by default';
        it(message, function() {
            this.collection.add([{}, {}, {}]);
            this.view.render();

            expect(this.view.$el).not.toContainText(
                'You haven\'t created any group configurations yet.'
            );
            expect(this.view.$('.group-configuration').length).toBe(3);
        });
    });

    describe('GroupConfigurationItem', function() {
        var groupConfigurationEditTpl = readFixtures(
                'group-configuration-edit.underscore'
            ),
            groupConfigurationDetailsTpl = readFixtures(
                'group-configuration-details.underscore'
            ), message;

        beforeEach(function() {
            setFixtures($('<script>', {
                id: 'group-configuration-edit-tpl',
                type: 'text/template'
            }).text(groupConfigurationEditTpl));
            setFixtures($('<script>', {
                id: 'group-configuration-details-tpl',
                type: 'text/template'
            }).text(groupConfigurationDetailsTpl));
            this.model = new GroupConfigurationModel({
                id: 0
            });
            this.collection = new GroupConfigurationSet([ this.model ]);
            this.view = new GroupConfigurationItem({
                model: this.model
            });
            this.view.render();
        });

        message = 'should render GroupConfigurationDetails view by default';
        it(message, function() {
            expect(
                this.view.$('.view-group-configuration-details').length
            ).toBe(1);
        });

        message = 'previous view should be replaced correctly';
        it(message, function() {
            expect(
                this.view.$('.view-group-configuration-details').length
            ).toBe(1);
            this.view.$('.action-edit .edit').click();
            expect(
                this.view.$('.view-group-configuration-edit').length
            ).toBe(1);
            expect(
                this.view.$('.view-group-configuration-details').length
            ).toBe(0);
        });
    });

    describe('GroupConfigurationsItem', function() {
        var groupConfigurationEditTpl = readFixtures(
            'group-configuration-edit.underscore'
        ), message;

        beforeEach(function() {
            setFixtures($('<script>', {
                id: 'group-configuration-edit-tpl',
                type: 'text/template'
            }).text(groupConfigurationEditTpl));
            this.collection = new GroupConfigurationSet();
            this.view = new GroupConfigurationsList({
                collection: this.collection
            });
            this.view.render();
        });

        message = 'should render GroupConfigurationDetails view by default';
        it(message, function() {
            this.collection.add([{}, {}, {}]);
            this.view.render();

            expect(
                this.view.$el.find('.view-group-configuration-details').length
            ).toBe(3);
        });
    });

    describe('GroupEdit', function() {
        var tpl = readFixtures('group-edit.underscore');

        beforeEach(function() {
            appendSetFixtures($('<script>', {
                id: 'group-edit-tpl',
                type: 'text/template'
            }).text(tpl));

            this.model = new GroupModel({
                name: 'Group A'
            });

            this.collection = new GroupSet([this.model]);

            this.view = new GroupEdit({
                model: this.model
            });
            spyOn(this.view, 'remove').andCallThrough();
        });

        describe('Basic', function () {
            it('can render', function() {
                this.view.render();
                expect(this.view.$('.group-name').val()).toBe('Group A');
                expect(this.view.$('.group-allocation')).toContainText('100%');
            });
        });

        describe('getGroupId', function () {
            it('returns correct ids', function () {
                expect(this.view.getGroupId(0)).toBe('A');
                expect(this.view.getGroupId(1)).toBe('B');
                expect(this.view.getGroupId(25)).toBe('Z');
                expect(this.view.getGroupId(702)).toBe('AAA');
                expect(this.view.getGroupId(704)).toBe('AAC');
                expect(this.view.getGroupId(475253)).toBe('ZZZZ');
                expect(this.view.getGroupId(475254)).toBe('AAAAA');
                expect(this.view.getGroupId(475279)).toBe('AAAAZ');
            });
        });
    });
});
