define [
    "backbone", "js/models/group_configuration", "js/collections/group_configuration",
    "js/models/group", "js/collections/group", "coffee/src/main"
],
(Backbone, GroupConfiguration, GroupConfigurationSet, Group, GroupSet, main) ->

  beforeEach ->
    @addMatchers
      toBeInstanceOf: (expected) ->
        return @actual instanceof expected


  describe "GroupConfiguration model", ->
    beforeEach ->
      main()
      @model = new GroupConfiguration()

    describe "Basic", ->
      it "should have an empty name by default", ->
        expect(@model.get("name")).toEqual("")

      it "should have an empty description by default", ->
        expect(@model.get("description")).toEqual("")

      it "should not show groups by default", ->
        expect(@model.get("showGroups")).toBeFalsy()

      it "should have a GroupSet with one group by default", ->
        groups = @model.get("groups")
        expect(groups).toBeInstanceOf(GroupSet)
        expect(groups.length).toEqual(2)
        expect(groups.at(0).isEmpty()).toBeTruthy()
        expect(groups.at(1).isEmpty()).toBeTruthy()

      it "should be empty by default", ->
        expect(@model.isEmpty()).toBeTruthy()

      it "should be able to reset itself", ->
        @model.set("name", "foobar")
        @model.reset()
        expect(@model.get("name")).toEqual("")

      it "should not be dirty by default", ->
        expect(@model.isDirty()).toBeFalsy()

      it "should be dirty after it's been changed", ->
        @model.set("name", "foobar")
        expect(@model.isDirty()).toBeTruthy()

      it "should not be dirty after calling setOriginalAttributes", ->
        @model.set("name", "foobar")
        @model.setOriginalAttributes()
        expect(@model.isDirty()).toBeFalsy()

    describe "Input/Output", ->
      deepAttributes = (obj) ->
        if obj instanceof Backbone.Model
            deepAttributes(obj.attributes)
        else if obj instanceof Backbone.Collection
            obj.map(deepAttributes);
        else if _.isArray(obj)
            _.map(obj, deepAttributes);
        else if _.isObject(obj)
            attributes = {};
            for own prop, val of obj
                attributes[prop] = deepAttributes(val)
            attributes
        else
            obj

      it "should match server model to client model", ->
        serverModelSpec = {
            "id": 10,
            "name": "My GroupConfiguration",
            "description": "Some description",
            "groups": [
                {"name": "Group 1"},
                {"name": "Group 2"},
            ]
        }
        clientModelSpec = {
            "id": 10,
            "name": "My GroupConfiguration",
            "description": "Some description",
            "showGroups": false,
            "groups": [{
                    "name": "Group 1"
                }, {
                    "name": "Group 2"
                }
            ]
        }

        model = new GroupConfiguration(serverModelSpec, {parse: true})
        expect(deepAttributes(model)).toEqual(clientModelSpec)
        expect(model.toJSON()).toEqual(serverModelSpec)

    describe "Validation", ->
      it "requires a name", ->
        model = new GroupConfiguration({name: ""})
        expect(model.isValid()).toBeFalsy()

      it "requires at least one group", ->
        model = new GroupConfiguration({name: "foo"})
        model.get("groups").reset()
        expect(model.isValid()).toBeFalsy()

      it "requires a valid group", ->
        group = new Group()
        group.isValid = -> false
        model = new GroupConfiguration({name: "foo"})
        model.get("groups").reset([group])
        expect(model.isValid()).toBeFalsy()

      it "requires all groups to be valid", ->
        group1 = new Group()
        group1.isValid = -> true
        group2 = new Group()
        group2.isValid = -> false
        model = new GroupConfiguration({name: "foo"})
        model.get("groups").reset([group1, group2])
        expect(model.isValid()).toBeFalsy()

      it "can pass validation", ->
        group = new Group()
        group.isValid = -> true
        model = new GroupConfiguration({name: "foo"})
        model.get("groups").reset([group])
        expect(model.isValid()).toBeTruthy()


  describe "Group model", ->
    beforeEach ->
      @model = new Group()

    describe "Basic", ->
      it "should have a name by default", ->
        expect(@model.get("name")).toEqual("")

      it "should be empty by default", ->
        expect(@model.isEmpty()).toBeTruthy()

    describe "Validation", ->
      it "requires a name", ->
        model = new Group({name: ""})
        expect(model.isValid()).toBeFalsy()

      it "can pass validation", ->
        model = new Group({name: "a"})
        expect(model.isValid()).toBeTruthy()


  describe "Group collection", ->
    beforeEach ->
      @collection = new GroupSet()

    it "is empty by default", ->
      expect(@collection.isEmpty()).toBeTruthy()

    it "is empty if all groups are empty", ->
      @collection.add([{}, {}, {}])
      expect(@collection.isEmpty()).toBeTruthy()

    it "is not empty if a group is not empty", ->
      @collection.add([{}, {name: "full"}, {}])
      expect(@collection.isEmpty()).toBeFalsy()
