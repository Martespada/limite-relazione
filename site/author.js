(() => {
  const dialog = document.getElementById('author-viewer');
  const image = document.getElementById('author-viewer-image');
  const title = document.getElementById('author-viewer-title');
  const original = document.getElementById('author-viewer-original');
  const close = document.getElementById('author-viewer-close');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  let previousOverflow;
  let opener;
  document.querySelectorAll('[data-author-poster]').forEach(link => {
    link.addEventListener('click', event => {
      // Preserve ordinary browser actions such as opening the original in a new tab.
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      title.textContent = link.dataset.authorPoster;
      image.alt = link.querySelector('img').alt;
      image.src = link.href;
      original.href = link.href;
      original.setAttribute('aria-label', 'Apri immagine originale: ' + link.dataset.authorPoster);
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      dialog.scrollTop = 0;
      close.focus();
    });
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow || '';
    image.removeAttribute('src');
    opener?.focus({preventScroll: true});
  });
})();
