 async function createProject(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await fetch("/" {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`HTTP Error Status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Project Created:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('projectForm');
    form.addEventListener('submit', createProject);
});

