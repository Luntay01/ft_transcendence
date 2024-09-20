document.addEventListener("DOMContentLoaded", function() {
	const apiResponseDiv = document.getElementById('api-response');
  
	fetch('http://localhost/api/ping/')
	  .then(response => response.json())
	  .then(data => {
		console.log(data);
		apiResponseDiv.textContent = data.message;
	  })
	  .catch(error => {
		console.error('Error:', error);
		apiResponseDiv.textContent = 'Failed to fetch API response';
	  });
  });