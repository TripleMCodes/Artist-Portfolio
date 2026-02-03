// Copy email button behavior (guard DOM lookups)
(function(){
  const btn = document.getElementById('copyEmail');
  const copied = document.getElementById('copied');
  const emailFallback = 'hello@xarya.com';

  if (btn) {
    btn.addEventListener('click', async () => {
      // try to extract an email from the button text if present
      const emailText = (btn.dataset && btn.dataset.email) || btn.textContent.replace(/\s+/g, ' ').trim() || emailFallback;
      try {
        if (!navigator.clipboard) throw new Error('clipboard API not available');
        await navigator.clipboard.writeText(emailText);
        if (copied) {
          copied.style.display = 'inline-block';
          setTimeout(() => copied.style.display = 'none', 1600);
        }
      } catch (err) {
        // fallback: open mailto
        window.location.href = 'mailto:' + encodeURIComponent(emailText || emailFallback);
      }
    });
  }

  // optional: log clicks to console for local testing (only if links exist)
  const clickableEls = document.querySelectorAll('.lt-links a, .lt-links button');
  if (clickableEls && clickableEls.length) {
    clickableEls.forEach(el => el.addEventListener('click', () => {
      try { console.log('Link click:', (el.href || el.textContent).toString()); } catch(e){}
    }));
  }
})();

// Hamburger navigation toggle: use class selector and guard nulls
const hamburger = document.getElementById('hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });
}