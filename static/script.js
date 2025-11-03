document.addEventListener('DOMContentLoaded', function(){
  const pdfInput = document.getElementById('pdfInput');
  const excelInput = document.getElementById('excelInput');
  const pdfName = document.getElementById('pdfName');
  const excelName = document.getElementById('excelName');
  const pdfDrop = document.getElementById('pdfDrop');
  const excelDrop = document.getElementById('excelDrop');
  const convertBtn = document.getElementById('convertBtn');
  const successCard = document.getElementById('successCard');
  const downloadBtn = document.getElementById('downloadBtn');
  const openLink = document.getElementById('openLink');

  let lastBlob = null;
  let lastUrl = null;

  function handleFileInput(input, nameEl){
    if(input.files && input.files[0]){
      nameEl.textContent = input.files[0].name;
    }
  }

  pdfInput.addEventListener('change', function(){ handleFileInput(pdfInput, pdfName); });
  excelInput.addEventListener('change', function(){ handleFileInput(excelInput, excelName); });

  function setupDrop(dropEl, inputEl, nameEl){
    dropEl.addEventListener('dragover', (e)=>{ e.preventDefault(); dropEl.classList.add('dragover'); });
    dropEl.addEventListener('dragleave', ()=>{ dropEl.classList.remove('dragover'); });
    dropEl.addEventListener('drop', (e)=>{
      e.preventDefault(); dropEl.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if(file){ inputEl.files = e.dataTransfer.files; nameEl.textContent = file.name; }
    });
  }
  setupDrop(pdfDrop, pdfInput, pdfName);
  setupDrop(excelDrop, excelInput, excelName);

  convertBtn.addEventListener('click', function(e){
    e.preventDefault();
    successCard.classList.add('hidden');
    if(!pdfInput.files.length || !excelInput.files.length){
      alert('Please select both PDF and Excel files.');
      return;
    }
    const fd = new FormData();
    fd.append('pdf', pdfInput.files[0]);
    fd.append('excel', excelInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/convert', true);
    xhr.responseType = 'blob';

    xhr.onloadstart = function(){ convertBtn.disabled = true; convertBtn.textContent = 'Processing...'; };
    xhr.upload.onprogress = function(e){ /* could update UI */ };
    xhr.onload = function(){
      convertBtn.disabled = false; convertBtn.textContent = 'Convert & Download ZIP';
      if(xhr.status === 200){
        lastBlob = xhr.response;
        if(lastUrl) URL.revokeObjectURL(lastUrl);
        lastUrl = URL.createObjectURL(lastBlob);
        downloadBtn.disabled = false;
        openLink.href = lastUrl;
        openLink.classList.remove('hidden');
        successCard.classList.remove('hidden');
      } else {
        
const reader = new FileReader();
  reader.onload = () => {
    try {
      const obj = JSON.parse(reader.result);
      if (obj.error === 'no_tokens' || obj.error === 'not_enough_tokens') {
        alert(obj.message); // (optional: replace with a card later)
      } else {
        alert(obj.error || 'Server error');
      }
    } catch(e) {
      alert('Server error');
    }
  };
  reader.readAsText(xhr.response);
        
        // try { const reader = new FileReader(); reader.onload = ()=>{ const obj = JSON.parse(reader.result); alert(obj.error||'Server error'); }; reader.readAsText(xhr.response); } catch(e){ alert('Server error'); }
      }
    };
    xhr.onerror = function(){ convertBtn.disabled = false; convertBtn.textContent = 'Convert & Download ZIP'; alert('Network error'); };
    xhr.send(fd);
  });

  downloadBtn.addEventListener('click', function(){
    if(!lastUrl) return;
    const a = document.createElement('a');
    a.href = lastUrl; a.download = 'zistal_output.zip'; document.body.appendChild(a); a.click(); a.remove();
  });
});


document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('convertForm');
  const pdfInput = document.getElementById('pdfInput');
  const excelInput = document.getElementById('excelInput');
  const convertBtn = document.getElementById('convertBtn');

  form.addEventListener('submit', async function(e){
    e.preventDefault();

    if (!pdfInput.files.length || !excelInput.files.length) {
      alert('Please select both PDF and Excel files.');
      return;
    }

    convertBtn.disabled = true;
    convertBtn.textContent = 'Processing...';

    const fd = new FormData();
    fd.append('pdf', pdfInput.files[0]);
    fd.append('excel', excelInput.files[0]);

    try {
      const res = await fetch('/convert', {
        method: 'POST',
        body: fd
      });

      convertBtn.disabled = false;
      convertBtn.textContent = 'Convert & Download ZIP';

      if (!res.ok) {
        const text = await res.text();
        let errorMsg = 'Conversion failed. Please check your files.';
        try {
          const obj = JSON.parse(text);
          if (obj.error) errorMsg = obj.error;
        } catch {}
        alert(errorMsg);
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'zistal_output.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Network error. Please try again.');
      convertBtn.disabled = false;
      convertBtn.textContent = 'Convert & Download ZIP';
    }
  });
});
