/* SkillLoop – main.js */

// ── Auto-dismiss alerts after 4s ──────────────────────────────
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity    = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// ── Confirm before delete/cancel ─────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// ── Active nav link ───────────────────────────────────────────
const path = window.location.pathname;
document.querySelectorAll('.nav-link, .sb-nav a').forEach(a => {
  if (a.getAttribute('href') === path) a.classList.add('active');
});

// ── Star rating picker ────────────────────────────────────────
document.querySelectorAll('.star-picker').forEach(picker => {
  const stars = picker.querySelectorAll('.pick-star');
  const input = document.getElementById(picker.dataset.input);
  stars.forEach((s, i) => {
    s.addEventListener('click', () => {
      if (input) input.value = i + 1;
      stars.forEach((x, j) => x.textContent = j <= i ? '⭐' : '☆');
    });
    s.addEventListener('mouseenter', () => {
      stars.forEach((x, j) => x.textContent = j <= i ? '⭐' : '☆');
    });
    s.addEventListener('mouseleave', () => {
      const val = input ? parseInt(input.value) : 0;
      stars.forEach((x, j) => x.textContent = j < val ? '⭐' : '☆');
    });
  });
});

// ── Character counter for textareas ──────────────────────────
document.querySelectorAll('textarea[maxlength]').forEach(ta => {
  const max = ta.getAttribute('maxlength');
  const counter = document.createElement('div');
  counter.className = 'text-sm text-muted';
  counter.style.textAlign = 'right';
  counter.textContent = `0 / ${max}`;
  ta.parentNode.insertBefore(counter, ta.nextSibling);
  ta.addEventListener('input', () => {
    counter.textContent = `${ta.value.length} / ${max}`;
  });
});

// ── Image preview on file input ───────────────────────────────
document.querySelectorAll('input[type=file][data-preview]').forEach(inp => {
  inp.addEventListener('change', () => {
    const file = inp.files[0];
    if (!file) return;
    const preview = document.getElementById(inp.dataset.preview);
    if (!preview) return;
    const reader = new FileReader();
    reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
    reader.readAsDataURL(file);
  });
});

// ── Wallet coin animation ─────────────────────────────────────
function animateNum(el, end, duration = 800) {
  const start = 0;
  const step  = end / (duration / 16);
  let   cur   = start;
  const timer = setInterval(() => {
    cur += step;
    if (cur >= end) { cur = end; clearInterval(timer); }
    el.textContent = Math.floor(cur).toLocaleString();
  }, 16);
}
document.querySelectorAll('[data-animate-num]').forEach(el => {
  const val = parseFloat(el.dataset.animateNum);
  if (!isNaN(val)) animateNum(el, val);
});

// ── Chat – auto scroll to bottom ─────────────────────────────
const chatMsgs = document.getElementById('chat-messages');
if (chatMsgs) chatMsgs.scrollTop = chatMsgs.scrollHeight;

// ── Chat – textarea auto-grow ─────────────────────────────────
document.querySelectorAll('.chat-input textarea').forEach(ta => {
  ta.addEventListener('input', () => {
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
  });
  ta.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const form = ta.closest('form');
      if (form) form.requestSubmit ? form.requestSubmit() : form.submit();
    }
  });
});

// ── SocketIO chat (if available) ─────────────────────────────
if (typeof io !== 'undefined') {
  const orderId  = document.body.dataset.orderId;
  const userId   = document.body.dataset.userId;
  const socket   = io();

  if (orderId) {
    socket.emit('join_room', { order_id: parseInt(orderId) });
  }
  if (userId) {
    socket.emit('join_user_room', { user_id: parseInt(userId) });
  }

  socket.on('new_message', data => {
    const msgs   = document.getElementById('chat-messages');
    const isMine = parseInt(data.sender_id) === parseInt(userId);
    const div    = document.createElement('div');
    div.className = `msg ${isMine ? 'mine' : 'theirs'}`;
    div.innerHTML = `
      <div class="msg-bubble">
        ${data.body ? `<div>${escHtml(data.body)}</div>` : ''}
        ${data.drive_link ? `<a href="${escHtml(data.drive_link)}" target="_blank" class="drive-link-chip">📎 View File</a>` : ''}
      </div>
      <div class="msg-meta">${data.sender_name} · just now</div>
    `;
    if (msgs) {
      msgs.appendChild(div);
      msgs.scrollTop = msgs.scrollHeight;
    }
  });

  socket.on('notification', data => {
    showToast(data.title, data.body);
    const cnt = document.querySelector('.nb .cnt');
    if (cnt) cnt.textContent = parseInt(cnt.textContent || 0) + 1;
  });
}

// ── Toast notification ────────────────────────────────────────
function showToast(title, body) {
  const t = document.createElement('div');
  t.style.cssText = `
    position:fixed;bottom:1.5rem;right:1.5rem;
    background:var(--navy);color:white;
    padding:1rem 1.25rem;border-radius:var(--radius-md);
    box-shadow:var(--shadow-lg);z-index:9999;
    max-width:320px;animation:slideIn .3s ease;
    border-left:4px solid var(--teal);
  `;
  t.innerHTML = `<div style="font-weight:700;margin-bottom:4px;">${escHtml(title)}</div>
                 <div style="font-size:.85rem;opacity:.8;">${escHtml(body)}</div>`;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = '.3s'; setTimeout(() => t.remove(), 300); }, 4000);
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Slide-in animation
const style = document.createElement('style');
style.textContent = `@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}`;
document.head.appendChild(style);