define(function (require) {

  //The parameters are radio buttons
  function RadioButtonGroup() {
    this.radioButtons = Array.prototype.slice.call(arguments, 0);

    // give the radio buttons pointers back to the group
    for (var i = 0; i < this.radioButtons.length; i++) {
      this.radioButtons[i].group = this;
    }
  }

  RadioButtonGroup.prototype.add = function () {
    var args = Array.prototype.slice.call(arguments, 0);
    var oldLen = this.radioButtons.length;
    this.radioButtons = this.radioButtons.concat(args);

    // give the radio buttons pointers back to the group
    for (var i = oldLen; i < this.radioButtons.length; i++) {
      this.radioButtons[i].group = this;
    }
  }

  RadioButtonGroup.prototype.remove = function (radioButton) {
    for (var i = 0; i < this.radioButtons.length; i ++) {
      if (this.radioButtons[i] === radioButton) {
        this.radioButtons.splice(i, 1);
      }
    }

    radioButton.group = null;
  };

  return RadioButtonGroup;
});