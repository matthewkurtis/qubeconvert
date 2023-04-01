const form = document.querySelector("form"),
fileInput = document.querySelector(".file-input"),
uploadButton = document.querySelector(".upload-button-area"),
uploadArea = document.querySelector('.uploading-area'),
downloadArea = document.querySelector(".download-area"),
downloadButton = document.querySelector(".download-area-content");

form.addEventListener("click", () =>{
  fileInput.click();
  while(downloadButton.hasChildNodes()){
    downloadButton.removeChild(downloadButton.firstChild); // Remove the first child of list everytime until the list is null.
  }
  downloadArea.style.display = 'none'; //Hide Download Button
});

fileInput.onchange = ({target})=>{
  let files = target.files;
  if(files){
    uploadFiles(files)
  }
}

async function uploadFiles(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('uploaded_files', file, file.name);
  }

  // Hide / Show Sections

  uploadArea.style.display = 'block'; // Show loading icon


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
      downloadButton.appendChild(downloadLink);
    } else {
      alert('Error uploading PDFs');
    }
  } catch (error) {
    console.error(error);
    alert('Error uploading PDFs');
  } finally {
    uploadArea.style.display = 'none'; // Hide loading icon
    downloadArea.style.display = 'block'; //Show Download Button
  }
}