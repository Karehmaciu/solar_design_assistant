// Theme switcher functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use prefer-color-scheme
    const currentTheme = localStorage.getItem('theme') || 
                        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    // Apply the theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Update the toggle if we're in dark mode
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    if (toggleSwitch) {
        toggleSwitch.checked = currentTheme === 'dark';
        
        // Listen for toggle changes
        toggleSwitch.addEventListener('change', function(e) {
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    
    // Existing dropdown functionality for share button
    const shareBtn = document.querySelector('.share-btn');
    const dropdown = document.getElementById('shareDropdown');
    
    if (shareBtn && dropdown) {
        shareBtn.addEventListener('click', function(event) {
            dropdown.classList.toggle('visible');
            event.preventDefault();
            event.stopPropagation();
        });
        
        window.addEventListener('click', function(event) {
            if (!event.target.matches('.share-btn')) {
                if (dropdown.classList.contains('visible')) {
                    dropdown.classList.remove('visible');
                }
            }
        });
    }
});