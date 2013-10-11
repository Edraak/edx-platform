###
TakeNote

Allows users to annotate videos
###


class TakeNote
  constructor: () ->
    # gather elements
    @$notes_taken = $("body").find("div[name='notestaken']")
    # @$note_text = $("body").find("input[name='notetaker']")
    @$note_time = $("body").find("input[name='currenttime']")
    @$takenote_btn = $("body").find("input[name='takenote']")
    @$noteform = $("body").find("#noteform")
    # @$player = $("div.video").data('state-obj').videoPlayer.player
    # TODO make this a real number
    #time_taken = "12"
    # attach click handlers

    @$takenote_btn.click (e) ->
      player = $("div.video").data('state-obj').videoPlayer.player
      $("input[name='currenttime']").val($("div.video").data('state-obj').videoPlayer.player.getCurrentTime())
      note_text = $("input[name='notetaker']")
      # alert "hello"
      # todo: insert call for retrieving time from page
      # sendtime = ??? presenttime - 5s
      # @$notes_taken.prepend(@$note_text.val() + " -- " + @$time_taken + "<br/>")
      currenttime = $("input[name='currenttime']").val()
      link_node = "<a href='javascript:void(0)'>" + note_text.val() + " (" + parseInt(currenttime) + ")</a>"
      $("#my_awesome_notes").append("<li>" + link_node + "</li>")
      $("#my_awesome_notes li").last().click (e) ->
        player.seekTo(currenttime) 

      url = @$noteform.data 'endpoint'

      $.ajax
        url: url
        data =
          "note_text": note_text.val()
          "timestamp": parseInt(currenttime)
        success (data) =>
          alert 'yayyyyy'


      





      # form = $("body").find("form[name='noteform']")
      # alert form.serialize()
      # $.ajax({
      #   type: "POST"
      #   url: form.attr('action')
      #   data: form.serialize()
      #   success: (response) ->
      #     alert('yay')
      #   })

        #time: time_taken
      #endbringback

      #$.ajax
      #  type: 'POST'
      #  dataType: 'json'
      #  url: @$btn_send.data 'endpoint'
      #  data: record_note
        #success: (data) => 
        #  TODO "Notes last saved at XX:XX AM/PM"
              
        #error: std_ajax_err => 
        #  TODO "Error saving notes

$(document).ready () -> new TakeNote 
