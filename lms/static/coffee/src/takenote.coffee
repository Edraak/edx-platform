###
TakeNote

Allows users to annotate videos
###

class TakeNote
  constructor: () ->
    # gather elements
    @$notes_taken = $("body").find("div[name='notestaken']'")
    @$note_text = $("body").find("textarea[name='notetaker']'")
    @$takenote = $("body").find("input[name='takenote']'")
    # TODO make this a real number
    #time_taken = "12"
    # attach click handlers

    @$takenote.click =>
      alert = "hello"
      # todo: insert call for retrieving time from page
      # sendtime = ??? presenttime - 5s
      @$notes_taken.prepend(@$note_text.val() + " -- " + @$time_taken + "<br/>")

      record_note =
        text: @$note_text.val()
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

@$stuff = @$("body").find("input[name='takenote']'")
@$stuff.click =>
  alert "gah"
alert "huh"