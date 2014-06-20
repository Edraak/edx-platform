define [
    "js/models/group_configuration", "js/models/course",
    "js/collections/group_configuration", "js/views/show_group_configurations",
    "js/views/list_group_configurations", "jasmine-stealth"
], (
    GroupConfigurationModel, Course, GroupConfigurationSet,
    ShowGroupConfigurations, ListGroupConfigurations
) ->
    beforeEach ->
      window.course = new Course({
        id: "5",
        name: "Course Name",
        url_name: "course_name",
        org: "course_org",
        num: "course_num",
        revision: "course_rev"
      });

      # remove this when we upgrade jasmine-jquery
      @addMatchers
        toContainText: (text) ->
          trimmedText = $.trim(@actual.text())
          if text and $.isFunction(text.test)
            return text.test(trimmedText)
          else
            return trimmedText.indexOf(text) != -1;

    afterEach ->
      delete window.course

    describe "ShowGroupConfigurations", ->
      tpl = readFixtures('show-group-configurations.underscore')

      beforeEach ->
        setFixtures($("<script>", {
            id: "show-group-configurations-tpl",
            type: "text/template"}).text(tpl)
        )
        @model = new GroupConfigurationModel({
          name: "Experiment",
          description: "Experiment Description",
          id: 0
        })
        spyOn(@model, "destroy").andCallThrough()
        @collection = new GroupConfigurationSet([@model])
        @view = new ShowGroupConfigurations({model: @model})

      describe "Basic", ->
        it "should render properly", ->
          @view.render()
          expect(@view.$el).toContainText("Experiment")
          expect(@view.$el).toContainText("Id: 0")

        it "should show groups appropriately", ->
          @model.get("groups").add([{}, {}, {}])
          @model.set('showGroups', false)
          @view.render().$(".show-groups").click()
          expect(@model.get('showGroups')).toBeTruthy()
          expect(@view.$el.find('.group').length).toBe(4)
          expect(@view.$el.find('.group-configuration-groups-count'))
            .not.toExist()
          expect(@view.$el.find('.group-configuration-description'))
            .toContainText('Experiment Description')

        it "should hide groups appropriately", ->
          @model.get("groups").add([{}, {}, {}])
          @model.set('showGroups', true)
          @view.render().$(".hide-groups").click()
          expect(@model.get('showGroups')).toBeFalsy()
          expect(@view.$el.find('.group').length).toBe(0)
          expect(@view.$el.find('.group-configuration-groups-count'))
            .toContainText('Contains 4 groups')
          expect(@view.$el.find('.group-configuration-description'))
            .not.toExist()


    describe "ListGroupConfigurations", ->
      noGroupConfigurationsTpl = readFixtures("no-group-configurations.underscore")

      beforeEach ->
        setFixtures($("<script>", {id: "no-group-configurations-tpl", type: "text/template"}).text(noGroupConfigurationsTpl))
        @showSpies = spyOnConstructor(window, "ShowGroupConfigurations", ["render"])
        @showSpies.render.andReturn(@showSpies) # equivalent of `return this`
        showEl = $("<li>")
        @showSpies.$el = showEl
        @showSpies.el = showEl.get(0)
        @collection = new GroupConfigurationSet()
        @view = new ListGroupConfigurations({collection: @collection})
        @view.render()

      it "should render the empty template if there are no group configurations", ->
        expect(@view.$el).toContainText(
          "You haven't created any group configurations yet."
        )
        expect(@view.$el).not.toContain(".new-button")
        expect(@showSpies.constructor).not.toHaveBeenCalled()

      it "should render ShowGroupConfigurations views by default", ->
        # add three empty group configurations to the collection
        @collection.add([{}, {}, {}])
        # render once and test
        @view.render()

        expect(@view.$el).not.toContainText(
          "You haven't created any group configurations yet."
        )
        expect(@view.$el.find('.group-configuration').length).toBe(3);
