    function getDownloadLink() {
        const requests = new XMLHttpRequest();
        if (!requests) {
          console.log('Failed to create XMLHttpRequest');
          return false;
        }
        requests.open('POST', `/API/v1/GUI/GetDownloadLink?file_path={{ dir_path + '/' + filename }}`);
        requests.send();
        requests.onreadystatechange = function() {
          if (requests.readyState === XMLHttpRequest.DONE) {
            if (requests.status === 200) {
              const downloadLink = document.getElementById('downloadLink');
              let responseLink = requests.responseText.replace(/['"]+/g, '');
              downloadLink.setAttribute("href", responseLink);
              downloadLink.onclick = null;
              downloadLink.textContent = 'GUI Download';
              const curlDownload = document.getElementById('curlcommand');
              curlDownload.setAttribute('style', 'visibility: visible;');
              curlDownload.setAttribute('data', responseLink);
            } else {
              console.log('Failed to Contact API. Check Status');
            }
          }
        }
    }
    function copyCurlCommand() {
        const curlDownload = document.getElementById('curlcommand');
        navigator.clipboard.writeText(curlDownload.data);
        curlDownload.textContent = 'Command Copied!';
    }