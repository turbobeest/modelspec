/* ModelSpec feedback control (MODEL-221).
 *
 * Every page built by the pipeline carries <a data-feedback-launch href="/feedback/">.
 * Without JavaScript it is a link to the feedback page. With it, it opens this
 * form in a dialog. The /feedback/ page also renders the form in place of
 * <div data-feedback-inline>. Nothing here sets a cookie or stores anything in
 * the browser; the only request is the POST (or DELETE) the person sends.
 */
(function () {
  "use strict";

  var DEFAULT_ENDPOINT = "https://api.modelspec.dev/v1/feedback";
  var RATINGS = [
    ["reliable", "Reliable"],
    ["unreliable", "Unreliable"],
    ["trustworthy", "Trustworthy"],
    ["untrustworthy", "Untrustworthy"],
    ["confusing", "Confusing"],
  ];
  var counter = 0;

  /* A local Worker can stand in for the real one, but only on a local page and
   * only for a local endpoint: a link cannot send a visitor's feedback elsewhere. */
  function endpoint() {
    var local = /^(localhost|127\.0\.0\.1)$/;
    if (!local.test(location.hostname)) return DEFAULT_ENDPOINT;
    var asked = new URLSearchParams(location.search).get("feedback_endpoint");
    if (!asked) return DEFAULT_ENDPOINT;
    try {
      var url = new URL(asked);
      return local.test(url.hostname) ? url.href : DEFAULT_ENDPOINT;
    } catch (e) {
      return DEFAULT_ENDPOINT;
    }
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      if (key === "text") node.textContent = attrs[key];
      else node.setAttribute(key, attrs[key]);
    });
    (children || []).forEach(function (child) {
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function call(method, body) {
    return fetch(endpoint(), {
      method: method,
      mode: "cors",
      credentials: "omit",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (response) {
      return response.json().then(
        function (payload) { return { ok: response.ok, payload: payload }; },
        function () { return { ok: false, payload: null, status: response.status }; }
      );
    });
  }

  function form(question) {
    var id = "ms-fb-" + ++counter;
    var fieldset = el("fieldset", { class: "ms-fb-ratings" }, [el("legend", { text: question })]);
    RATINGS.forEach(function (pair) {
      fieldset.appendChild(el("label", {}, [
        el("input", { type: "radio", name: id + "-rating", value: pair[0] }),
        pair[1],
      ]));
    });
    var note = el("textarea", { maxlength: "1000", rows: "3", "aria-describedby": id + "-privacy" });
    var trying = el("input", { type: "text", maxlength: "300", "aria-describedby": id + "-privacy" });
    var send = el("button", { type: "submit", class: "ms-fb-send", text: "Send feedback" });
    var status = el("p", { class: "ms-fb-status", role: "status", tabindex: "-1" });
    var node = el("form", { class: "ms-fb-form", "aria-label": question }, [
      fieldset,
      el("label", { class: "ms-fb-field" }, [
        el("span", {}, ["Anything else? ", el("em", { text: "(optional)" })]), note,
      ]),
      el("label", { class: "ms-fb-field" }, [
        el("span", {}, ["What were you trying to decide? ", el("em", { text: "(optional)" })]), trying,
      ]),
      el("p", { id: id + "-privacy", class: "ms-fb-privacy" }, [
        "No account and no key. Please don't include prompts, keys or personal details. ",
        el("a", { href: "/feedback/#privacy", text: "What we keep" }),
      ]),
      el("div", { class: "ms-fb-actions" }, [send]),
      status,
    ]);

    function say(text, isError) {
      status.textContent = text;
      status.setAttribute("role", isError ? "alert" : "status");
      status.focus();
    }

    node.addEventListener("submit", function (event) {
      event.preventDefault();
      var chosen = node.querySelector("input[type=radio]:checked");
      if (!chosen) {
        say("Choose one of the five first.", true);
        return;
      }
      var body = { rating: chosen.value, client: "page", page: location.pathname };
      if (note.value.trim()) body.note = note.value.trim();
      if (trying.value.trim()) body.trying_to_decide = trying.value.trim();
      send.disabled = true;
      send.textContent = "Sending…";
      call("POST", body).then(function (answer) {
        send.disabled = false;
        send.textContent = "Send feedback";
        var p = answer.payload || {};
        if (!answer.ok) {
          say((p.error && p.error.message) || "Feedback could not be sent.", true);
          return;
        }
        Array.prototype.forEach.call(node.querySelectorAll("fieldset, label, .ms-fb-actions, .ms-fb-privacy"),
          function (child) { child.hidden = true; });
        var removed = (p.redacted || []).map(function (k) { return k.replace("_", " "); });
        var text = p.status === "recorded"
          ? "Thank you. Your feedback was recorded."
          : "Thank you. Feedback storage is not switched on yet, so nothing was kept.";
        if (removed.length) text += " We removed what looked like " + removed.join(", ") + " before it reached us.";
        say(text, false);
        if (p.status === "recorded" && p.receipt) {
          var undo = el("button", { type: "button", class: "ms-fb-undo", text: "Undo and delete it" });
          undo.addEventListener("click", function () {
            call("DELETE", { receipt: p.receipt }).then(function (gone) {
              undo.remove();
              say(gone.ok ? "Deleted. Nothing of it is kept." : "It could not be deleted.", !gone.ok);
            });
          });
          node.appendChild(undo);
        }
      }, function () {
        send.disabled = false;
        send.textContent = "Send feedback";
        say("Feedback could not be sent. Check your connection and try again.", true);
      });
    });
    return node;
  }

  function dialog() {
    var box = el("dialog", { class: "ms-fb-dialog", "aria-label": "Feedback" });
    var close = el("button", { type: "button", class: "ms-fb-close", "aria-label": "Close feedback", text: "Close" });
    close.addEventListener("click", function () { box.close(); });
    box.appendChild(el("div", { class: "ms-fb-head" }, [el("strong", { text: "Feedback" }), close]));
    box.appendChild(form("What did you think of this page?"));
    box.addEventListener("close", function () { box.remove(); });
    document.body.appendChild(box);
    if (typeof box.showModal === "function") box.showModal();
    else box.setAttribute("open", "");
    return box;
  }

  function start() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-feedback-launch]"), function (link) {
      link.setAttribute("role", "button");
      link.setAttribute("aria-haspopup", "dialog");
      link.addEventListener("click", function (event) {
        event.preventDefault();
        dialog();
      });
      link.addEventListener("keydown", function (event) {
        if (event.key === " ") {
          event.preventDefault();
          dialog();
        }
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-feedback-inline]"), function (slot) {
      slot.replaceChildren(form(slot.getAttribute("data-question") || "What did you think of ModelSpec?"));
    });
  }

  window.ModelSpecFeedback = { open: dialog, endpoint: endpoint };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
