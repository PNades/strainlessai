/*
 * StrainlessAI v1 — presentation-only helpers for the main page.
 * Reads the DOM the app already writes and sets CSS variables / data attributes.
 * It calls no app functions and changes no app state.
 */
(function () {
  'use strict';

  var root = document.documentElement;
  var dock = document.querySelector('.input-container');
  var recorder = document.getElementById('recordingInterface');
  var statusEl = document.getElementById('recordingStatus');
  var timerEl = document.querySelector('.rec-timer');
  var chatMessages = document.getElementById('chatMessages');

  /* 1. Dock height -> --dock-h, so content and scrollIntoView clear the dock. */
  if (dock) {
    var setDockHeight = function () {
      root.style.setProperty('--dock-h', dock.offsetHeight + 'px');
    };
    setDockHeight();
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(setDockHeight).observe(dock);
    } else {
      window.addEventListener('resize', setDockHeight);
    }
  }

  /* 2. On-screen keyboard -> --kb. iOS keeps the layout viewport when the keyboard opens,
   *    so lift the fixed dock by the part of the layout viewport the keyboard covers.
   *    Android (interactive-widget=resizes-content) resizes the layout viewport, so kb = 0. */
  var vv = window.visualViewport;
  if (vv) {
    var setKeyboard = function () {
      var zoomed = vv.scale && Math.abs(vv.scale - 1) > 0.01;
      var kb = zoomed ? 0 : Math.round(window.innerHeight - vv.height - vv.offsetTop);
      if (kb < 1) kb = 0;
      root.style.setProperty('--kb', kb + 'px');
      if (kb > 0) root.setAttribute('data-kb', '');
      else root.removeAttribute('data-kb');
    };
    vv.addEventListener('resize', setKeyboard);
    vv.addEventListener('scroll', setKeyboard);
    setKeyboard();
  }

  /* 3. Recorder state from the status text the app writes. */
  var MAX_SECONDS = 9; // the app auto-stops after 9 s
  var tick = null;
  var startedAt = 0;
  var lastState = 'idle';

  function stateFromText(text) {
    if (text.indexOf('Listening') === 0) return 'recording';
    if (text.indexOf('Recording complete') === 0) return 'recorded';
    if (text.indexOf('Analyzing') === 0) return 'processing';
    if (text.indexOf('Analysis complete') === 0) return 'done';
    if (text.indexOf('Error') === 0 || text.indexOf('No recording') === 0) return 'error';
    return 'idle';
  }

  function showElapsed(seconds) {
    var s = Math.min(MAX_SECONDS, Math.floor(seconds));
    if (timerEl) timerEl.textContent = '0:0' + s + ' / 0:0' + MAX_SECONDS;
    recorder.style.setProperty('--rec-frac', Math.min(1, seconds / MAX_SECONDS).toFixed(3));
  }

  function applyRecorderState() {
    var state = stateFromText((statusEl.textContent || '').trim());
    if (state === lastState) return;

    if (state === 'recording') {
      startedAt = performance.now();
      showElapsed(0);
      clearInterval(tick);
      tick = setInterval(function () {
        showElapsed((performance.now() - startedAt) / 1000);
      }, 100);
    } else {
      clearInterval(tick);
      tick = null;
      if (state === 'recorded' && lastState === 'recording') {
        showElapsed((performance.now() - startedAt) / 1000); // keep how long was captured
      } else if (state !== 'recorded') {
        recorder.style.setProperty('--rec-frac', '0');
      }
    }

    recorder.setAttribute('data-state', state);
    if (state === 'processing') recorder.setAttribute('aria-busy', 'true');
    else recorder.removeAttribute('aria-busy');
    lastState = state;
  }

  if (recorder && statusEl) {
    recorder.setAttribute('data-state', 'idle');
    new MutationObserver(applyRecorderState)
      .observe(statusEl, { childList: true, characterData: true, subtree: true });
  }

  /* 4. Flag bot error replies so they get the error message style. */
  var ERROR_PREFIXES = ['Error', 'Sorry, I encountered an error'];
  var flagQueued = false;

  function flagErrors() {
    flagQueued = false;
    var items = chatMessages.querySelectorAll('.chat-message.bot .message-content');
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      if (el.querySelector('.classification-result, .typing-indicator')) continue;
      var text = (el.textContent || '').trim();
      var isError = ERROR_PREFIXES.some(function (p) { return text.indexOf(p) === 0; });
      el.classList.toggle('is-error', isError);
    }
  }

  if (chatMessages) {
    new MutationObserver(function () {
      if (!flagQueued) {
        flagQueued = true;
        requestAnimationFrame(flagErrors);
      }
    }).observe(chatMessages, { childList: true, characterData: true, subtree: true });
  }
})();
