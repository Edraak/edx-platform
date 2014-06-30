# -*- coding: utf-8 -*-
describe "NewPostView", ->
    beforeEach ->
        setFixtures(
            """
            <div class="discussion-body">
                <div class="discussion-column">
                  <article class="new-post-article" style="display: block;"></article>
                </div>
            </div>

            <script aria-hidden="true" type="text/template" id="new-post-template">
                <div class="inner-wrapper">
                    <form class="new-post-form">
                        <div class="control-group">
                            <div class="control-items">
                                <span class="control-label">
                                   Organized Into:
                                </span>
                                <span class="control-controls">
                                    <div class="form-topic-drop">
                                        <a href="#" aria-labelledby="topic-dropdown-label" class="topic_dropdown_button">select...<span class="drop-arrow" aria-hidden="true">▾</span></a>
                                        <div class="topic_menu_wrapper">
                                            <div class="topic_menu_search" role="menu">
                                                <label class="sr" for="browse-topic-newpost">Filter List</label>
                                                <input type="text" id="browse-topic-newpost" class="form-topic-drop-search-input" placeholder="Filter discussion areas">
                                           </div>
                                           <ul class="topic_menu" role="menu"><%= topics_html %></ul>
                                       </div>
                                   </div>
                               </span>
                           </div>
                        </div>
                    </form>
                </div>
            </script>

            <script aria-hidden="true" type="text/template" id="new-post-menu-entry-template">
                <li role="menuitem"><a href="#" class="topic" data-discussion_id="<%- id %>" aria-describedby="topic-name-span-<%- id %>" cohorted="<%- is_cohorted %>"><%- text %></a></li>
            </script>

            <script aria-hidden="true" type="text/template" id="new-post-menu-category-template">
                <li role="menuitem">
                    <a href="#"><span class="category-menu-span"><%- text %></span></a>
                    <ul role="menu"><%= entries %></ul>
                </li>
            </script>
            """
        )
        window.$$course_id = "edX/999/test"
        spyOn(DiscussionUtil, "makeWmdEditor")
        @discussion = new Discussion([], {pages: 1})
        @view = new NewPostView(
          el: $(".new-post-article"),
          collection: @discussion,
          course_settings: new DiscussionCourseSettings({
            "category_map": {
              "subcategories": {
                "Basic Question Types": {
                  "subcategories": {},
                  "children": ["Selection From Options"],
                  "entries": {
                    "Selection From Options": {
                      "sort_key": null,
                      "is_cohorted": true,
                      "id": "cba3e4cd91d0466b9ac50926e495b76f"
                    }
                  },
                },
              },
              "children": ["Basic Question Types"],
              "entries": {}
            },
            "allow_anonymous": true,
            "allow_anonymous_to_peers": true
          }),
          mode: "tab"
        )
        @view.render()
        @parent_category_text = "Basic Question Types"
        @selected_option_text = "Selection From Options"

    describe "Drop down works correct", ->

      it "completely show parent category and sub-category", ->
        complete_text = @parent_category_text + " / " + @selected_option_text
        selected_text_width = @view.getNameWidth(complete_text)
        @view.maxNameWidth = selected_text_width + 1
        @view.$el.find( "ul.topic_menu li[role='menuitem'] > a" )[1].click()
        dropdown_text = @view.$el.find(".form-topic-drop > a").text()
        expect(complete_text+' ▾').toEqual(dropdown_text)

      it "completely show just sub-category", ->
        complete_text = @parent_category_text + " / " + @selected_option_text
        selected_text_width = @view.getNameWidth(complete_text)
        @view.maxNameWidth = selected_text_width - 10
        @view.$el.find( "ul.topic_menu li[role='menuitem'] > a" )[1].click()
        dropdown_text = @view.$el.find(".form-topic-drop > a").text()
        expect(dropdown_text.indexOf("…")).toEqual(0)
        expect(dropdown_text).toContain(@selected_option_text)

      it "partially show sub-category", ->
        parent_width = @view.getNameWidth(@parent_category_text)
        complete_text = @parent_category_text + " / " + @selected_option_text
        selected_text_width = @view.getNameWidth(complete_text)
        @view.maxNameWidth = selected_text_width - parent_width
        @view.$el.find( "ul.topic_menu li[role='menuitem'] > a" )[1].click()
        dropdown_text = @view.$el.find(".form-topic-drop > a").text()
        expect(dropdown_text.indexOf("…")).toEqual(0)
        expect(dropdown_text.lastIndexOf("…")).toBeGreaterThan(0)

      it "broken span doesn't occur", ->
        complete_text = @parent_category_text + " / " + @selected_option_text
        selected_text_width = @view.getNameWidth(complete_text)
        @view.maxNameWidth = @view.getNameWidth(@selected_option_text) + 100
        @view.$el.find( "ul.topic_menu li[role='menuitem'] > a" )[1].click()
        dropdown_text = @view.$el.find(".form-topic-drop > a").text()
        expect(dropdown_text.indexOf("/ span>")).toEqual(-1)
