(function (requirejs, require, define) {
define(function () {

  var color = {
    //Old palette
    background: "rgb(0, 51, 102)", //0.0, 0.2, 0.4
    black: "rgb(0, 0, 0)", //0.0
    lodarkgray: "rgb(26, 26, 26)", //0.1 = 25.5
    darkgray: "rgb(51, 51, 51)", //0.2
    lomidgray: "rgb(102, 102, 102)", //0.4
    midgray: "rgb(128, 128, 128)", //0.5 = 127.5
    himidgray: "rgb(153, 153, 153)", //0.6
    litegray: "rgb(204, 204, 204)", //0.8
    white: "rgb(255, 255, 255)", //1.0

    red: "rgb(255, 0, 0)",
    green: "rgb(0, 255, 0)",
    blue: "rgb(0, 0, 255)",
    yellow: "rgb(255, 255, 0)",
    cyan: "rgb(0, 255, 255)",
    magenta: "rgb(255, 0, 255)",
    orange: "rgb(255, 153, 0)", //1.0, 0.6, 0.0
    purple: "rgb(199, 63, 188)",


    //Solarized palette: http://ethanschoonover.com/solarized
    base03: "#002b36",
    base02: "#073642",
    base015: "#30535c",
    base01: "#586e75",
    base00: "#657b83",
    base0: "#839496",
    base1: "#93a1a1",
    base2: "#eee8d5",
    base3: "#fdf6e3",
    solYellow: "#b58900",
    solOrange: "#cb4b16",
    solRed: "#dc322f",
    solMagenta: "#d33682",
    solViolet: "#6c71c4",
    solBlue: "#268bd2",
    solCyan: "#2aa198",
    solGreen: "#859900",
    lightblue: "#00bfff", //or "#95c6e9"
    lightyellow: "#ffcf48",
    lightgreen: "#1df914", //or "#c3cd82"
    lightmagenta: "#ff3656"
  };

  return color;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));