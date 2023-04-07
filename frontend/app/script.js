const form = document.querySelector("form"),
fileInput = document.querySelector(".file-input"),
uploadButton = document.querySelector(".upload-button-area"),
uploadArea = document.querySelector('.uploading-area'),
downloadArea = document.querySelector(".download-area"),
downloadButton = document.querySelector(".download-area-content");

form.addEventListener("click", () =>{
  fileInput.click();
  while(downloadButton.hasChildNodes()){
    downloadButton.removeChild(downloadButton.firstChild);
  }
  downloadArea.style.display = 'none';
});

form.addEventListener("dragover", (e) => {
  e.preventDefault();
  form.classList.add("dragover");
});

form.addEventListener("dragleave", () => {
  form.classList.remove("dragover");
});

form.addEventListener("drop", (e) => {
  e.preventDefault();
  form.classList.remove("dragover");
  const files = e.dataTransfer.files;
  if (files) {
    uploadFiles(files);
  }
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


  uploadArea.style.display = 'block';


  try {
    const response = await fetch('https://api.qubeconvert.com/uploadfiles/', {
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
      downloadArea.style.display = 'block';
    } else {
      alert("Something went wrong... \nMake sure your file is a Qube Statement PDF");
    }
  } catch (error) {
    console.error(error);
    alert(error);
  } finally {
    uploadArea.style.display = 'none';
    
  }
}