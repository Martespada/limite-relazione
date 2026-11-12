(() => {
  'use strict';
  const dialog = document.getElementById('media-viewer');
  let opener, previousOverflow = '';
  if (dialog && typeof dialog.showModal === 'function') {
    document.addEventListener('click', event => {
      const link = event.target.closest('[data-author-poster],[data-media]');
      if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      document.getElementById('media-title').textContent = link.dataset.authorPoster || link.dataset.media;
      const image = document.getElementById('media-image');
      image.alt = link.querySelector('img')?.alt || link.dataset.media || link.dataset.authorPoster;
      image.src = link.href;
      document.getElementById('media-original').href = link.href;
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      dialog.scrollTop = 0;
      dialog.querySelector('[data-close-media]').focus();
    });
    dialog.querySelector('[data-close-media]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {
      document.body.style.overflow = previousOverflow;
      document.getElementById('media-image').removeAttribute('src');
      if (opener?.isConnected) opener.focus({preventScroll:true});
    });
  }
  const input = document.getElementById('reading-search');
  if (input) {
    const type = document.getElementById('reading-type');
    const items = [...document.querySelectorAll('.v2-archive-item')];
    const normalize = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    const query = new URLSearchParams(location.search);
    input.value = query.get('q') || '';
    type.value = ['all','articolo','pdf'].includes(query.get('formato')) ? query.get('formato') : 'all';
    function filter() {
      const words = normalize(input.value).trim().split(/\s+/).filter(Boolean);
      let total = 0, pdf = 0, article = 0;
      items.forEach(item => {
        item.hidden = !((type.value === 'all' || item.dataset.kind === type.value) && words.every(w => normalize(item.dataset.search).includes(w)));
        if (!item.hidden) { total++; item.dataset.kind === 'pdf' ? pdf++ : article++; }
      });
      document.getElementById('reading-count').textContent = `${total} ${total === 1 ? 'lettura' : 'letture'}`;
      document.getElementById('reading-empty').hidden = total !== 0;
      document.querySelector('.v2-archive-grid').hidden = article === 0;
      document.querySelector('.v2-pdf-section').hidden = pdf === 0;
      const url = new URL(location.href);
      input.value.trim() ? url.searchParams.set('q',input.value.trim()) : url.searchParams.delete('q');
      type.value !== 'all' ? url.searchParams.set('formato',type.value) : url.searchParams.delete('formato');
      history.replaceState(null,'',url.pathname + url.search + url.hash);
    }
    input.addEventListener('input',filter); type.addEventListener('change',filter); filter();
  }
})();
