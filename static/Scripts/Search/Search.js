    // Capture form submit
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('myForm');
        form.addEventListener('submit', function(event) {
            event.preventDefault();

            // Capture form data
            const formData = new FormData(form);
            const searchParams = new URLSearchParams();

            for (const pair of formData) {
                searchParams.append(pair[0], pair[1]);
            }

            // POST data to the server
            fetch('/API/v1/FileBrowser/GUI/ArchiveSearch', {
                method: 'POST',
                body: searchParams,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }).then(response => response.json())
              .then(data => {
                let resultsHtml = '<ul>';
                for (const result of data) {
                    resultsHtml += `<li><a href="/FileBrowser/FileInfo?file_path=${result}">${result}</a></li>`;
                }
                resultsHtml += '</ul>';

                document.getElementById('results').innerHTML = resultsHtml;
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    });