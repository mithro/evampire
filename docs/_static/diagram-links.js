/*
 * On narrow screens diagrams are scaled down to the width of the page
 * column, which can make their labels hard to read. Add a link under each
 * Graphviz or SVG diagram that opens the diagram on its own, where the
 * reader can zoom it.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
document.addEventListener("DOMContentLoaded", function () {
  var diagrams = document.querySelectorAll(
    "article object.graphviz, article img[src$='.svg']");
  diagrams.forEach(function (el) {
    var url = el.tagName === "OBJECT" ? el.data : el.src;
    if (!url) {
      return;
    }
    var link = document.createElement("a");
    link.href = url;
    link.className = "diagram-full-size";
    link.textContent = "Open diagram at full size";
    el.insertAdjacentElement("afterend", link);
  });
});
