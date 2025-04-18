// Dropdown functionality for share button
document.addEventListener('DOMContentLoaded', function() {
  // Get the share button and dropdown elements
  const shareBtn = document.querySelector('.share-btn');
  const dropdown = document.getElementById('shareDropdown');
  
  // Toggle dropdown when share button is clicked
  if (shareBtn) {
    shareBtn.addEventListener('click', function(event) {
      // Toggle visibility class
      dropdown.classList.toggle('visible');
      
      // Prevent form submission
      event.preventDefault();
      event.stopPropagation();
    });
  }
  
  // Close dropdown when clicking elsewhere on the page
  window.addEventListener('click', function(event) {
    if (!event.target.matches('.share-btn')) {
      if (dropdown && dropdown.classList.contains('visible')) {
        dropdown.classList.remove('visible');
      }
    }
  });
});