document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('roasting-form');
    const urlInput = document.getElementById('website');
    const responseDiv = document.getElementById('roast');
    const responseText = document.getElementById('the-actual-thing');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const url = urlInput.value;

        // TODO: add api url
        fetch('https://localhost:8080', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        })
            .then(response => response.text())
            .then(data => {
                responseText.textContent = data;
                responseDiv.style.display = 'block';
                form.style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);
                responseText.textContent = 'your portfolio so bad that i dont even know how to roast it';
                responseDiv.style.display = 'block';
                form.style.display = 'none';
            });
    });
});