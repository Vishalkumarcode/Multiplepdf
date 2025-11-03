document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('loginForm');
  const err = document.getElementById('error');
  form.addEventListener('submit', async function(e){
    e.preventDefault();
    err.textContent = '';
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username, password})
      });
      if(res.ok){
        const j = await res.json();
        if(j.success){ window.location = '/'; return; }
      }
      const data = await res.json();
      err.textContent = data.error || 'Login failed';
    } catch(errc){
      err.textContent = 'Network error';
    }
  });
});