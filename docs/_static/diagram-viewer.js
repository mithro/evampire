/*
 * Diagram viewer. Clicking a diagram opens it over the whole browser
 * window, where the reader can zoom in and pan around to read small labels.
 *
 *   wheel or pinch       zoom about the pointer
 *   drag                 pan
 *   click the diagram    zoom in, when the whole diagram is showing
 *   double click         back to the whole diagram, when zoomed in
 *   + - 0 and arrows     zoom in, zoom out, whole diagram, pan
 *   Esc or the backdrop  close
 *
 * Each diagram is wrapped in a link to its SVG file, so it can be reached
 * with the keyboard, and a click with Ctrl, Shift or the middle button
 * still opens the file in a new tab.
 *
 * SPDX-License-Identifier: Apache-2.0
 */
(function () {
  "use strict";

  var DIAGRAMS = "article object.graphviz, article img[src$='.svg'], " +
    "article img[src*='wavedrom-']";

  // Zoom is measured against the scale at which the whole diagram fits the
  // window, so 1 is "fit" on every screen size.
  var MAX_ZOOM = 10;       // furthest zoom in
  var CLICK_ZOOM = 3;      // zoom after a click on the fitted diagram
  var BUTTON_STEP = 1.5;   // one press of + or -
  var PAN_STEP = 80;       // pixels moved by one arrow key press
  var MARGIN = 16;         // pixels kept clear around the fitted diagram
  var TAP_SLOP = 6;        // pointer travel below this is a click, not a drag
  var DOUBLE_TAP_MS = 350;

  var dialog, stage, image, caption, openLink, zoomInButton, zoomOutButton,
    fitButton;
  // Size of the diagram in its own units, and the scale that fits it.
  var natural = {w: 1, h: 1}, fit = 1;
  // Scale in screen pixels per diagram unit, and the position of the
  // diagram's top left corner within the stage.
  var view = {s: 1, x: 0, y: 0};
  var pointers = new Map();
  var travel = 0, downTarget = null, tapPending = false;
  var lastTap = {t: 0, x: 0, y: 0};

  function atFit() {
    return view.s <= fit * 1.001;
  }

  // Keep the diagram on screen: centred along an axis where it is smaller
  // than the stage, and otherwise never dragged past its own edge.
  function clampAxis(position, size, room) {
    var low = room - MARGIN - size;
    var high = MARGIN;
    return low > high ? (room - size) / 2 :
      Math.min(high, Math.max(low, position));
  }

  function render() {
    var w = natural.w * view.s;
    var h = natural.h * view.s;
    view.x = clampAxis(view.x, w, stage.clientWidth);
    view.y = clampAxis(view.y, h, stage.clientHeight);
    // Setting the size, not a CSS scale, makes the browser redraw the SVG
    // at the new size, so lines and text stay sharp at every zoom.
    image.style.width = w + "px";
    image.style.height = h + "px";
    image.style.transform =
      "translate(" + view.x + "px, " + view.y + "px)";
    stage.classList.toggle("is-zoomed", !atFit());
    setDisabled(zoomOutButton, atFit());
    setDisabled(fitButton, atFit());
    setDisabled(zoomInButton, view.s >= fit * MAX_ZOOM * 0.999);
  }

  // A button that can do nothing is marked with aria-disabled, not the
  // disabled attribute. Disabling the focused button would move the focus
  // out of the viewer, and the next Tab would start from the top.
  function setDisabled(el, disabled) {
    el.setAttribute("aria-disabled", disabled ? "true" : "false");
  }

  function measureFit() {
    fit = Math.min(
      (stage.clientWidth - 2 * MARGIN) / natural.w,
      (stage.clientHeight - 2 * MARGIN) / natural.h);
    fit = fit > 0 ? fit : 1;
  }

  function showWhole() {
    measureFit();
    view.s = fit;
    render();
  }

  // Zoom by a factor while keeping the diagram point under (px, py) still.
  function zoomAbout(px, py, factor) {
    var scale = Math.min(fit * MAX_ZOOM, Math.max(fit, view.s * factor));
    view.x = px - (px - view.x) * scale / view.s;
    view.y = py - (py - view.y) * scale / view.s;
    view.s = scale;
    render();
  }

  // The + and - buttons and keys zoom about the centre of the stage.
  function zoomIn() {
    zoomAbout(stage.clientWidth / 2, stage.clientHeight / 2, BUTTON_STEP);
  }

  function zoomOut() {
    zoomAbout(stage.clientWidth / 2, stage.clientHeight / 2,
      1 / BUTTON_STEP);
  }

  function pan(dx, dy) {
    view.x += dx;
    view.y += dy;
    render();
  }

  function stagePoint(event) {
    var box = stage.getBoundingClientRect();
    return {x: event.clientX - box.left, y: event.clientY - box.top};
  }

  function onWheel(event) {
    event.preventDefault();
    // Firefox reports a mouse wheel in lines, not pixels.
    var delta = event.deltaY * (event.deltaMode === 1 ? 16 : 1);
    // A pinch on a trackpad arrives as a wheel event with ctrlKey set and
    // small deltas.
    var rate = event.ctrlKey ? 0.01 : 0.0015;
    var point = stagePoint(event);
    zoomAbout(point.x, point.y, Math.exp(-delta * rate));
  }

  function onPointerDown(event) {
    if (event.pointerType === "mouse" && event.button !== 0) {
      return;
    }
    if (pointers.size === 0) {
      travel = 0;
      downTarget = event.target;
      tapPending = false;
    }
    pointers.set(event.pointerId, stagePoint(event));
    stage.setPointerCapture(event.pointerId);
    stage.classList.add("is-dragging");
  }

  function onPointerMove(event) {
    var before = pointers.get(event.pointerId);
    if (!before) {
      return;
    }
    var now = stagePoint(event);
    if (pointers.size === 1) {
      travel += Math.abs(now.x - before.x) + Math.abs(now.y - before.y);
      pointers.set(event.pointerId, now);
      pan(now.x - before.x, now.y - before.y);
      return;
    }
    // Two fingers: zoom by the change in their distance, about the point
    // midway between them, and pan by the movement of that point.
    var other;
    pointers.forEach(function (point, id) {
      if (id !== event.pointerId) {
        other = point;
      }
    });
    var oldDistance = Math.hypot(before.x - other.x, before.y - other.y);
    var newDistance = Math.hypot(now.x - other.x, now.y - other.y);
    view.x += (now.x - before.x) / 2;
    view.y += (now.y - before.y) / 2;
    travel = Infinity;
    pointers.set(event.pointerId, now);
    zoomAbout((now.x + other.x) / 2, (now.y + other.y) / 2,
      oldDistance > 0 ? newDistance / oldDistance : 1);
  }

  function onPointerUp(event) {
    if (!pointers.delete(event.pointerId) || pointers.size > 0) {
      return;
    }
    stage.classList.remove("is-dragging");
    tapPending = event.type === "pointerup" && travel < TAP_SLOP;
  }

  // A tap is acted on at the click that follows it, not at the pointerup.
  // Closing at the pointerup would let the browser deliver that click to
  // whatever part of the page lies under the finger.
  function onClick(event) {
    if (tapPending) {
      tapPending = false;
      onTap(stagePoint(event), downTarget);
    }
  }

  function onTap(point, target) {
    if (target !== image) {
      dialog.close();
      return;
    }
    var now = Date.now();
    if (atFit()) {
      zoomAbout(point.x, point.y, CLICK_ZOOM);
      lastTap.t = 0;  // the next tap is not the second half of a double tap
      return;
    }
    var isDouble = now - lastTap.t < DOUBLE_TAP_MS &&
      Math.hypot(point.x - lastTap.x, point.y - lastTap.y) < 30;
    lastTap = {t: now, x: point.x, y: point.y};
    if (isDouble) {
      lastTap.t = 0;
      showWhole();
    }
  }

  // Keys are taken from the document before any other script sees them.
  // The focus is not always inside the viewer, and Sphinx's own Esc
  // handler would otherwise stop the browser from closing the dialog.
  function onKeyDown(event) {
    if (!dialog.open || event.ctrlKey || event.metaKey || event.altKey) {
      return;
    }
    var actions = {
      "+": zoomIn, "=": zoomIn, "-": zoomOut, "_": zoomOut,
      "0": showWhole,
      "Escape": function () { dialog.close(); },
      "ArrowLeft": function () { pan(PAN_STEP, 0); },
      "ArrowRight": function () { pan(-PAN_STEP, 0); },
      "ArrowUp": function () { pan(0, PAN_STEP); },
      "ArrowDown": function () { pan(0, -PAN_STEP); }
    };
    if (Object.prototype.hasOwnProperty.call(actions, event.key)) {
      event.preventDefault();
      event.stopPropagation();
      actions[event.key]();
    }
  }

  function button(label, text, action) {
    var el = document.createElement("button");
    el.type = "button";
    el.textContent = text;
    el.title = label;
    el.setAttribute("aria-label", label);
    el.addEventListener("click", function () {
      if (el.getAttribute("aria-disabled") !== "true") {
        action();
      }
    });
    return el;
  }

  function build() {
    dialog = document.createElement("dialog");
    dialog.className = "diagram-viewer";
    dialog.setAttribute("aria-label", "Diagram viewer");

    var bar = document.createElement("div");
    bar.className = "diagram-viewer-bar";
    var hint = document.createElement("span");
    hint.className = "diagram-viewer-hint";
    hint.textContent = "Scroll or pinch to zoom, drag to pan";
    zoomOutButton = button("Zoom out", "−", zoomOut);
    zoomInButton = button("Zoom in", "+", zoomIn);
    fitButton = button("Show the whole diagram", "Fit", showWhole);
    openLink = document.createElement("a");
    openLink.textContent = "Open file";
    openLink.title = "Open the diagram file in a new tab";
    openLink.target = "_blank";
    openLink.rel = "noopener";
    var closeButton = button("Close", "✕", function () {
      dialog.close();
    });
    closeButton.autofocus = true;
    bar.append(hint, zoomOutButton, zoomInButton, fitButton, openLink,
      closeButton);

    stage = document.createElement("div");
    stage.className = "diagram-viewer-stage";
    image = document.createElement("img");
    image.className = "diagram-viewer-image";
    image.draggable = false;
    stage.appendChild(image);

    caption = document.createElement("div");
    caption.className = "diagram-viewer-caption";

    dialog.append(bar, stage, caption);
    document.body.appendChild(dialog);

    stage.addEventListener("wheel", onWheel, {passive: false});
    stage.addEventListener("pointerdown", onPointerDown);
    stage.addEventListener("pointermove", onPointerMove);
    stage.addEventListener("pointerup", onPointerUp);
    stage.addEventListener("pointercancel", onPointerUp);
    stage.addEventListener("click", onClick);
    document.addEventListener("keydown", onKeyDown, true);
    dialog.addEventListener("close", function () {
      pointers.clear();
      stage.classList.remove("is-dragging");
      document.documentElement.classList.remove("diagram-viewer-open");
    });
    // Keep the whole diagram fitted, or the zoomed view on screen, when
    // the window changes size or a phone is turned.
    new ResizeObserver(function () {
      if (!dialog.open || image.hidden) {
        return;
      }
      var wasFitted = atFit();
      measureFit();
      if (wasFitted) {
        view.s = fit;
      }
      zoomAbout(0, 0, 1);  // brings the scale within the new limits
    }).observe(stage);
  }

  function captionOf(diagram) {
    var figure = diagram.closest("figure");
    var text = figure && figure.querySelector("figcaption");
    if (!text) {
      return "";
    }
    text = text.cloneNode(true);
    text.querySelectorAll("a.headerlink").forEach(function (link) {
      link.remove();
    });
    return text.textContent.trim();
  }

  function show(diagram, url) {
    if (!dialog) {
      build();
    }
    var shown = diagram.getBoundingClientRect();
    image.hidden = true;
    image.onload = function () {
      // An SVG with no width and height of its own reports no natural
      // size; use the size it has in the page instead.
      natural.w = image.naturalWidth || shown.width || 1;
      natural.h = image.naturalHeight || shown.height || 1;
      image.hidden = false;
      showWhole();
    };
    image.alt = diagram.tagName === "OBJECT" ?
      diagram.textContent.trim() : diagram.alt;
    image.removeAttribute("src");
    image.src = url;
    openLink.href = url;
    caption.textContent = captionOf(diagram);
    caption.hidden = !caption.textContent;
    document.documentElement.classList.add("diagram-viewer-open");
    dialog.showModal();
  }

  function attach(diagram) {
    var url = diagram.tagName === "OBJECT" ? diagram.data : diagram.src;
    if (!url) {
      return;
    }
    // Sphinx already links a scaled image to its file. A diagram inside
    // any other link keeps that link.
    var link = diagram.closest("a");
    if (link && !link.classList.contains("image-reference")) {
      return;
    }
    if (!link) {
      link = document.createElement("a");
      link.href = url;
      diagram.parentNode.insertBefore(link, diagram);
      link.appendChild(diagram);
    }
    link.classList.add("diagram-zoom");
    if (diagram.tagName === "OBJECT") {
      // The link's name comes from its content, and an <object> has none.
      link.classList.add("diagram-zoom-object");
      var name = captionOf(diagram);
      link.setAttribute("aria-label",
        name ? "Enlarge diagram: " + name : "Enlarge diagram");
    }
    link.addEventListener("click", function (event) {
      if (event.button !== 0 || event.ctrlKey || event.metaKey ||
          event.shiftKey || event.altKey ||
          typeof HTMLDialogElement !== "function") {
        return;  // let the browser open the file
      }
      event.preventDefault();
      show(diagram, url);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(DIAGRAMS).forEach(attach);
  });
})();
