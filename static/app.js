document.querySelectorAll('form[data-endpoint]').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button');
    const status = form.querySelector('.status');
    const output = form.querySelector('pre');
    const started = performance.now();
    button.disabled = true;
    status.dataset.error = 'false';
    status.textContent = 'Sending request…';
    output.textContent = '';
    try {
      const options = { method: form.dataset.method };
      if (options.method === 'POST') {
        const fields = new FormData(form);
        const payload = {};
        for (const [name, value] of fields) {
          // Parsing individual fields preserves JSON types for server validation.
          // Keep the seed literal intact to avoid rounding 64-bit integers in JS.
          if (name !== 'seed') payload[name] = JSON.parse(value);
        }
        let body = JSON.stringify(payload);
        if (fields.has('seed')) {
          const seed = fields.get('seed').trim();
          if (!/^-?(0|[1-9][0-9]*)$/.test(seed)) {
            throw new Error('Seed must be an integer without leading zeros.');
          }
          body = body.slice(0, -1) + ',"seed":' + seed + '}';
        }
        options.headers = { 'Content-Type': 'application/json' };
        options.body = body;
      }
      const response = await fetch(form.dataset.endpoint, options);
      const text = await response.text();
      try { output.textContent = JSON.stringify(JSON.parse(text), null, 2); }
      catch { output.textContent = text || '(Empty response)'; }
      status.dataset.error = String(!response.ok);
      status.textContent = `HTTP ${response.status} · ${Math.round(performance.now() - started)} ms`;
    } catch (error) {
      status.dataset.error = 'true';
      status.textContent = 'Request failed';
      output.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
});
