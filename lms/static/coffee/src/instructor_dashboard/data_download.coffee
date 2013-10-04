# Data Download Section

# imports from other modules.
# wrap in (-> ... apply) to defer evaluation
# such that the value can be defined later than this assignment (file load order).
plantTimeout = -> window.InstructorDashboard.util.plantTimeout.apply this, arguments
std_ajax_err = -> window.InstructorDashboard.util.std_ajax_err.apply this, arguments


# Data Download Section
class DataDownload
  constructor: (@$section) ->
    # gather elements
    @$display                = @$section.find '.data-display'
    @$display_text           = @$display.find '.data-display-text'
    @$display_table          = @$display.find '.data-display-table'
    @$request_response_error = @$display.find '.request-response-error'
    @$list_studs_btn = @$section.find("input[name='list-profiles']")
    @$list_anon_btn = @$section.find("input[name='list-anon-ids']")
    @$grade_config_btn = @$section.find("input[name='dump-gradeconf']")
    @$grade_data_btn = @$section.find("input[name='download-grades']")
    @$ans_dist_btn = @$section.find("input[name='list-answer-distributions']")


    get_table_button = (e, button, error_message) =>
      button.click (e) =>
      url = button.data 'endpoint'

      # handle case of raw grades
      if $(e.target).data 'raw'
        url += '/raw'

      # handle csv special case
      if $(e.target).data 'csv'
        # redirect the document to the csv file.
        url += '/csv'
        location.href = url
      else
        @clear_display()
        @$display_table.text 'Loading...'

        # fetch grades list
        $.ajax
          dataType: 'json'
          url: url
          error: std_ajax_err =>
            @clear_display()
            @$request_response_error.text error_message
          success: (data) =>
            @clear_display()

            # display on a SlickGrid
            options =
              enableCellNavigation: true
              enableColumnReorder: false
              forceFitColumns: true

            columns = ({id: feature, field: feature, name: feature} for feature in data.queried_features)
            grid_data = data.student_data

            $table_placeholder = $ '<div/>', class: 'slickgrid'
            @$display_table.append $table_placeholder
            grid = new Slick.Grid($table_placeholder, grid_data, columns, options)
            # grid.autosizeColumns()

    # attach click handlers

    # The list-anon case is always CSV
    @$list_anon_btn.click (e) =>
      url = @$list_anon_btn.data 'endpoint'
      location.href = url


    # this handler binds to both the download
    # and the csv button
    @$grade_data_btn.click (e) =>
      get_table_button(e, @$grade_data_btn, "Error getting student grades.")


    # this handler binds to both the download
    # and the csv button
    @$list_studs_btn.click (e) =>
      get_table_button(e, @$list_studs_btn, "Error getting student list.")


    @$grade_config_btn.click (e) =>
      url = @$grade_config_btn.data 'endpoint'
      # display html from grading config endpoint
      $.ajax
        dataType: 'json'
        url: url
        error: std_ajax_err =>
          @clear_display()
          @$request_response_error.text "Error getting grading configuration."
        success: (data) =>
          @clear_display()
          @$display_text.html data['grading_config_summary']

    # answer-distribution is always a csv
    @$ans_dist_btn.click (e) =>
      url = @$ans_dist_btn.data 'endpoint'
      $.ajax
        dataType: 'json'
        url: url
        error: std_ajax_err =>
          @clear_display()
          @$request_response_error.text "Error getting distributions."
        success: (data) =>
          @clear_display()
                    # display on a SlickGrid
          options =
            enableCellNavigation: true
            enableColumnReorder: false
            forceFitColumns: true

          columns = ({id: feature, field: feature, name: feature} for feature in data.queried_features)
          grid_data = data.data

          $table_placeholder = $ '<div/>', class: 'slickgrid'
          @$display_table.append $table_placeholder
          grid = new Slick.Grid($table_placeholder, grid_data, columns, options)
          # grid.autosizeColumns()



  clear_display: ->
    @$display_text.empty()
    @$display_table.empty()
    @$request_response_error.empty()


# export for use
# create parent namespaces if they do not already exist.
# abort if underscore can not be found.
if _?
  _.defaults window, InstructorDashboard: {}
  _.defaults window.InstructorDashboard, sections: {}
  _.defaults window.InstructorDashboard.sections,
    DataDownload: DataDownload
