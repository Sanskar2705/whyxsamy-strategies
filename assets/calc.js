// Decay calculator for strategy note 04: the stock goes up by `swing`% then back down to where it started, repeatedly.
// A leveraged daily product multiplies each day's move by `lev`. No fees or financing costs.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (v) { return "₹" + v.toFixed(2); };
  function run() {
    var s = parseFloat($("swing").value) / 100;
    var days = Math.max(2, Math.round(parseFloat($("days").value) / 2) * 2);
    var lev = parseFloat($("lev").value);
    var out = $("calc-out");
    if (!(s > 0) || !(lev >= 1) || !(days >= 2)) { out.textContent = "Enter a positive swing, at least 2 days and leverage of 1 or more."; return; }
    var down = 1 / (1 + s) - 1; // the % fall that brings the stock back to start
    var stock = 100, fund = 100;
    for (var d = 0; d < days; d++) {
      var m = d % 2 === 0 ? s : down;
      stock *= 1 + m;
      fund *= Math.max(0, 1 + lev * m);
    }
    var lost = 100 - fund;
    out.innerHTML =
      "<div class='grid2'>" +
      "<div class='stat'><div class='label'>Stock after " + days + " days</div><div class='num'>" + fmt(stock) + "</div></div>" +
      "<div class='stat'><div class='label'>" + lev + "x daily fund</div><div class='num " + (fund < 100 ? "c-red" : "c-green") + "'>" + fmt(fund) + "</div></div>" +
      "</div><p class='c-muted'>Each day: up " + (s * 100).toFixed(2) + "%, then down " + (-down * 100).toFixed(2) +
      "%. The fund " + (lost > 0 ? "lost " + lost.toFixed(2) + "% while the stock went nowhere." : "did not lose in this setting.") + "</p>";
  }
  ["swing", "days", "lev"].forEach(function (id) { $(id).addEventListener("input", run); });
  run();
})();
