// Future JavaScript functionality can be added here.
// For now, this file is ready for any interactive features you may want to implement later.

// Tab Switching
// Wait for the DOM to be fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTabs);
} else {
    initializeTabs();
}

function initializeTabs() {
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    // Add click handlers to each tab button
    tabButtons.forEach(button => {
        button.onclick = function() {
            const tabName = this.getAttribute('data-tab');
            
            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Activate the clicked tab
            this.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        };
    });
}
