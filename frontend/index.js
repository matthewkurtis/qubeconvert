async function uploadPDF(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('uploaded_files', file, file.name);
  }

  const loadingIcon = document.getElementById('loadingIcon');
  loadingIcon.style.display = 'block'; // Show loading icon

  try {
    const response = await fetch('http://localhost:8000/uploadfiles/', {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      const csvData = await response.text();
      const blob = new Blob([csvData], {type: 'text/csv'});
      const csvUrl = URL.createObjectURL(blob);

      // extract filename from response headers using regex
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition ? contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)[1].replace(/['"]/g, '') : 'download.csv';

      // create link element to trigger download
      const downloadLink = document.createElement('a');
      downloadLink.href = csvUrl;
      downloadLink.download = filename;
      downloadLink.innerHTML = 'Download CSV';
      document.body.appendChild(downloadLink);
    } else {
      alert('Error uploading PDFs');
    }
  } catch (error) {
    console.error(error);
    alert('Error uploading PDFs');
  } finally {
    loadingIcon.style.display = 'none'; // Hide loading icon
  }
}

  uploadButton.addEventListener('click', () => {
    const files = pdfInput.files;
    if (files.length > 0) {
      uploadPDF(files);
    }
  });