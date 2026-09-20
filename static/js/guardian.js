(() => {
  if (!document.querySelector('link[href="/static/css/app.css"]')) {
    const stylesheet = document.createElement('link'); stylesheet.rel = 'stylesheet'; stylesheet.href = '/static/css/app.css'; document.head.appendChild(stylesheet);
  }
  const routes = {home:'/', 'black-list':'/black-list/', companies:'/companies/', 'background-verification':'/verification/', 'verification-result':'/verification/', 'warning-news':'/warning-news/', 'about-us':'/about/', contact:'/contact/', login:'/login/', 'person-profile':'/black-list/', 'company-profile':'/companies/', 'news-detail':'/warning-news/'};
  document.querySelectorAll('[data-path]').forEach((link) => { const target = routes[link.dataset.path]; if (target) link.setAttribute('href', target); });
})();
