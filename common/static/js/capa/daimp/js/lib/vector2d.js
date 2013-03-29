(function (requirejs, require, define) {
define(function () {

  function Vector2d(x, y) {
    this.x = x;
    this.y = y;
  }

  Vector2d.prototype.mag = function () {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  };

  Vector2d.prototype.phase = function () {
    var ang = Math.atan2(this.y, this.x);
    if (ang >= 0.0) {
      return ang;
    }  
    else {
      return 2.0 * Math.PI + ang;
    }  
  };

  Vector2d.prototype.scale = function (s) {
    this.x *= s;
    this.y *= s;
  };

  return Vector2d;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));