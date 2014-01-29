$(function() {
  
  // Set up on page load
  $("a.zoomable").each(function() {
    var smallImageObject = $(this).children();
    var largeImageSRC = $(this).attr('href');
    
    // if contents of zoomable link is image and large image link exists: setup modal
    if (smallImageObject.is('img') && largeImageSRC) {
      var smallImageHTML = $(this).html();
      var largeImageHTML = '<img alt="" src="' + largeImageSRC + '" />';
      var imageModalHTML =
        '<div class="imageModal-link">' +
          smallImageHTML +
          '<i class="icon-fullscreen icon-3x"></i>' +
        '</div>' +
        '<div class="imageModal"><div class="imageModal-content">' +
          '<div class="imageModal-imgWrapper">' + largeImageHTML + '</div>' +
          '<i class="icon-remove icon-3x"></i>' +
          '<div class="imageModal-zoom"><i class="icon-zoom-in icon-3x"></i><i class="icon-zoom-out icon-3x"></i></div></div>' +
        '</div>';
      $(this).replaceWith(imageModalHTML);
    }
  });
  var draggie = [];
  $('.imageModal-imgWrapper img').each(function(index) {
    draggie[index] = new Draggabilly( this, {
      containment: true
    });
    draggie[index].disable();
    $(this).attr("id", "draggie-" + index);
  });


  // Opening and closing image modal on clicks
  $(".imageModal-link").click(function() {
    $(this).siblings(".imageModal").show();
    $(this).siblings(".imageModal").find(".imageModal-imgWrapper img").css({top: 0, left: 0, });
    $(this).siblings(".imageModal").find(".imageModal-imgWrapper").css({left: 0, top: 0, width: 'auto', height: 'auto'});
    $('html').css({overflow: 'hidden'});
  });
  
  // variable to detect when modal is being "hovered".
  var imageModalImageHover = false;
  $(".imageModal-content img, .imageModal-content .imageModal-zoom").hover(function() {
    imageModalImageHover = true;
  }, function() {
    imageModalImageHover = false;
  });
  
  // Click outside of modal to close it.
  $(".imageModal").click(function() {
    if (!imageModalImageHover){
      $(this).hide();
      var currentDraggie = $('.imageModal-content .imageModal-imgWrapper img', this).removeClass('zoomed').attr('id').split('-');
      draggie[currentDraggie[1]].disable();
      $('html').css({overflow: 'auto'});
    }
  });
  
  // Click close icon to close modal.
  $(".imageModal-content i.icon-remove").click(function() {
    $(this).closest(".imageModal").hide();
    var currentDraggie = $(this).siblings('.imageModal-imgWrapper').children('img').removeClass('zoomed').attr('id').split('-');
    draggie[currentDraggie[1]].disable();
    $('html').css({overflow: 'auto'});
  });


  // zooming image in modal and allow it to be dragged
  // Make sure it always starts zero position for below calcs to work
  
  $(".imageModal-content .imageModal-zoom i").click(function() {
    var mask = $(this).closest(".imageModal-content");
    
    var img = $(this).closest(".imageModal").find("img");
    var currentDraggie = img.attr('id').split('-');
    
    if ($(this).hasClass('icon-zoom-in')) {
      img.addClass('zoomed');
      
      var imgWidth   = img.width();
      var imgHeight  = img.height();
      
      var imgContainerOffsetLeft = imgWidth - mask.width();
      var imgContainerOffsetTop = imgHeight - mask.height();
      var imgContainerWidth = imgWidth + imgContainerOffsetLeft;
      var imgContainerHeight = imgHeight + imgContainerOffsetTop;
      
      img.parent().css({left: -imgContainerOffsetLeft, top: -imgContainerOffsetTop, width: imgContainerWidth, height: imgContainerHeight});
      img.css({top: imgContainerOffsetTop / 2, left: imgContainerOffsetLeft / 2});
      
      draggie[currentDraggie[1]].enable();
      
    } else if ($(this).hasClass('icon-zoom-out')) {
      img.css({top: 0, left: 0, }).removeClass('zoomed');
      draggie[currentDraggie[1]].disable();
      img.parent().css({left: 0, top: 0, width: 'auto', height: 'auto'});
    }
  });
});