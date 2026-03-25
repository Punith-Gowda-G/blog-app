/* ── INKWELL BLOG — main.js ── */

// ── Delete confirmation ──────────────────────
document.querySelectorAll('.delete-form').forEach(form => {
  form.addEventListener('submit', function (e) {
    const entity = this.dataset.entity || 'item';
    const title = this.dataset.title || `this ${entity}`;
    if (!confirm(`Delete "${title}"? This cannot be undone.`)) {
      e.preventDefault();
    }
  });
});

// Toggle comment edit forms
document.querySelectorAll('.comment-edit-toggle').forEach(button => {
  button.addEventListener('click', function () {
    const targetId = this.dataset.target;
    const form = document.getElementById(targetId);
    if (!form) return;

    const isHidden = form.classList.toggle('hidden');
    this.textContent = isHidden ? 'Edit' : 'Cancel';
  });
});

// ── Word count on textarea ───────────────────
const textarea = document.getElementById('content');
const wordCount = document.getElementById('word-count');

function updateWordCount() {
  const text = textarea.value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  wordCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
}

if (textarea && wordCount) {
  updateWordCount();
  textarea.addEventListener('input', updateWordCount);
}

// ── Auto-dismiss flash messages ──────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.4s, transform 0.4s';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// ── Smooth search on category pill click ─────
document.querySelectorAll('.pill').forEach(pill => {
  pill.addEventListener('click', function (e) {
    e.preventDefault();
    const url = this.href;
    document.querySelector('.posts-grid, .empty-state')?.classList.add('fading');
    setTimeout(() => { window.location.href = url; }, 150);
  });
});

// Live image preview for cover image URL field
const imageUrlInput = document.getElementById('image_url');
const imagePreview = document.getElementById('image-preview');

if (imageUrlInput && imagePreview) {
  let debounceTimer;
  imageUrlInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const url = imageUrlInput.value.trim();
      if (url) {
        const img = new Image();
        img.onload = () => {
          imagePreview.innerHTML = `<img src="${url}" alt="Cover preview" />`;
          imagePreview.style.display = 'block';
        };
        img.onerror = () => {
          imagePreview.innerHTML = '';
          imagePreview.style.display = 'none';
        };
        img.src = url;
      } else {
        imagePreview.innerHTML = '';
        imagePreview.style.display = 'none';
      }
    }, 500);
  });
}
