// Vercel Web Analytics initialization script
(function() {
  // Initialize the queue
  window.va = window.va || function() {
    (window.vaq = window.vaq || []).push(arguments);
  };

  // Load the analytics script
  var script = document.createElement('script');
  script.src = '/_vercel/insights/script.js';
  script.defer = true;
  script.setAttribute('data-sdkn', '@vercel/analytics');
  script.setAttribute('data-sdkv', '1.6.1');
  
  script.onerror = function() {
    console.log('[Vercel Web Analytics] Failed to load analytics script. Please ensure Web Analytics is enabled for your Vercel project.');
  };
  
  document.head.appendChild(script);
})();
