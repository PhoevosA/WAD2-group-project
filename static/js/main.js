// CSRF Helper
function getCookie(name) {
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

// Like button
document.querySelectorAll('.like-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const url = btn.dataset.url;
    const postId = btn.dataset.postId;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        }
      });
      const data = await res.json();
      btn.classList.toggle('liked', data.is_liked);
      const heart = btn.querySelector('path');
      if (heart) heart.setAttribute('fill', data.is_liked ? 'currentColor' : 'none');
      const counter = document.getElementById('likes-' + postId);
      if (counter) counter.textContent = data.likes_count + ' like' + (data.likes_count !== 1 ? 's' : '');
    } catch (e) { console.error(e); }
  });
});

// Bookmark button
document.querySelectorAll('.bookmark-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const url = btn.dataset.url;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        }
      });
      const data = await res.json();
      btn.classList.toggle('bookmarked', data.is_bookmarked);
      const path = btn.querySelector('path');
      if (path) path.setAttribute('fill', data.is_bookmarked ? 'currentColor' : 'none');
    } catch (e) { console.error(e); }
  });
});

// Follow toggle
document.querySelectorAll('.follow-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const url = btn.dataset.url;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        }
      });
      const data = await res.json();
      btn.classList.toggle('following', data.is_following);
      btn.textContent = data.is_following ? 'Following' : 'Follow';
      const counter = document.getElementById('followers-count');
      if (counter) counter.textContent = data.followers_count;
    } catch (e) { console.error(e); }
  });
});

// Post menus
document.querySelectorAll('.menu-trigger').forEach(trigger => {
  trigger.addEventListener('click', e => {
    e.stopPropagation();
    const menu = trigger.closest('.post-menu');
    document.querySelectorAll('.post-menu.open').forEach(m => {
      if (m !== menu) m.classList.remove('open');
    });
    menu.classList.toggle('open');
  });
});

document.addEventListener('click', () => {
  document.querySelectorAll('.post-menu.open').forEach(m => m.classList.remove('open'));
});

// Auto dismiss flash messages
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 0.4s, transform 0.4s';
    msg.style.opacity = '0';
    msg.style.transform = 'translateX(100px)';
    setTimeout(() => msg.remove(), 400);
  }, 3500);
});
