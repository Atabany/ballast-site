// The home page's hero loop. The file is attached only here, so under reduced motion or Save-Data
// (or with no JavaScript) the poster stays and nothing is downloaded unless someone presses Play.
(function () {
  var video = document.getElementById('hero-video');
  var button = document.getElementById('hero-toggle');
  if (!video || !button) return;
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var saveData = navigator.connection && navigator.connection.saveData;
  var attached = false;

  function attach() {
    video.src = video.dataset.src;
    attached = true;
  }

  function show(playing) {
    button.textContent = playing ? 'Pause' : 'Play';
    button.setAttribute('aria-label', playing ? 'Pause the background video' : 'Play the background video');
  }

  if (motion.matches || saveData) {
    video.removeAttribute('autoplay');
    show(false);
  } else {
    attach();
    show(true);
  }

  motion.addEventListener('change', function () {
    if (motion.matches) { video.pause(); show(false); }
  });

  button.addEventListener('click', function () {
    if (!attached) attach();
    if (video.paused) {
      var started = video.play();
      if (started && started.catch) started.catch(function () { show(false); });
      show(true);
    } else {
      video.pause();
      show(false);
    }
  });
  button.hidden = false;
})();
