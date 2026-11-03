// The if-then plan builder. Nothing here touches the network; the page's security policy
// (connect-src 'none') would block it if it tried. Plans stay in memory unless the user
// ticks "keep", and then only in this browser's localStorage.
(function () {
  'use strict';
  var KEY = 'ballast-urge-plans';
  var $ = function (id) { return document.getElementById(id); };
  var form = $('builder'), cards = $('cards'), status = $('status');
  var ifText = $('if-text'), thenText = $('then-text'), whyText = $('why-text'), remember = $('remember');
  var printBtn = $('print-btn'), copyBtn = $('copy-btn'), clearBtn = $('clear-btn');
  var blank = cards.querySelector('[data-blank]');
  var plans = [];

  // The starters live in the server-rendered table, so there's one copy of them.
  var triggers = [].map.call(document.querySelectorAll('#starters tbody tr'), function (row) {
    return {
      name: row.getAttribute('data-trigger'),
      ifText: row.getAttribute('data-if'),
      thens: [].map.call(row.querySelectorAll('li'), function (li) { return li.textContent; })
    };
  });

  function storageGet() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }
  function save() {
    try {
      if (remember.checked && plans.length) { localStorage.setItem(KEY, JSON.stringify(plans)); }
      else { localStorage.removeItem(KEY); }
    } catch (e) { /* Private mode can refuse storage; the page still works. */ }
  }

  function choose(trigger) {
    ifText.value = trigger.ifText;
    var box = $('then-starters');
    box.textContent = '';
    trigger.thens.forEach(function (t) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = t;
      b.addEventListener('click', function () { thenText.value = t; thenText.focus(); });
      box.appendChild(b);
    });
  }

  function line(cls, text) {
    var p = document.createElement('p');
    p.className = cls;
    p.textContent = text;
    return p;
  }

  function render() {
    cards.textContent = '';
    if (!plans.length) { cards.appendChild(blank); }
    plans.forEach(function (plan, i) {
      var c = document.createElement('div');
      c.className = 'card-plan';
      c.appendChild(line('if', plan.ifText));
      c.appendChild(line('then', 'then ' + plan.thenText));
      if (plan.why) { c.appendChild(line('why', 'Because: ' + plan.why)); }
      var rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'rm no-print';
      rm.textContent = 'Remove';
      rm.setAttribute('aria-label', 'Remove plan: ' + plan.ifText);
      rm.addEventListener('click', function () { plans.splice(i, 1); save(); render(); say('Removed.'); });
      c.appendChild(rm);
      cards.appendChild(c);
    });
    var any = plans.length > 0;
    copyBtn.hidden = !any;
    clearBtn.hidden = !any;
  }

  function say(text) { status.textContent = text; }

  function asText() {
    return plans.map(function (p) {
      return p.ifText + ' then ' + p.thenText + (p.why ? '\nBecause: ' + p.why : '');
    }).join('\n\n');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var i = ifText.value.trim(), t = thenText.value.trim();
    if (!i || !t) { say('Write both the "if" and the "then".'); (i ? thenText : ifText).focus(); return; }
    t = t.replace(/^then\s+/i, '');
    plans.push({ ifText: i, thenText: t, why: whyText.value.trim() });
    thenText.value = '';
    whyText.value = '';
    save();
    render();
    say('Added to your sheet below.');
  });
  remember.addEventListener('change', function () {
    save();
    say(remember.checked ? 'Kept in this browser only.' : 'Not kept. Removed from this browser.');
  });
  printBtn.addEventListener('click', function () { window.print(); });
  copyBtn.addEventListener('click', function () {
    if (!navigator.clipboard) { say('Copying is not available here. Select the text instead.'); return; }
    navigator.clipboard.writeText(asText()).then(function () { say('Copied.'); }, function () { say('Copying was blocked. Select the text instead.'); });
  });
  clearBtn.addEventListener('click', function () { plans = []; save(); render(); say('Cleared.'); });

  // The chips are server-rendered so the page doesn't shift when this script runs.
  [].forEach.call(document.querySelectorAll('#chips input'), function (input) {
    input.addEventListener('change', function () { choose(triggers[Number(input.value)]); });
  });
  var kept = storageGet();
  if (Array.isArray(kept) && kept.length) { plans = kept.filter(function (p) { return p && p.ifText && p.thenText; }); remember.checked = true; }
  render();
})();
