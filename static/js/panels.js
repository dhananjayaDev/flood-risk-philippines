// Panels JavaScript functionality

// Panel management
let currentPanel = null;

// Initialize panels
document.addEventListener('DOMContentLoaded', function() {
    initializePanels();
    initializeSearch();
    initializeNotifications();
    
    // Make functions globally available
    window.performSearch = performSearch;
    window.openSearchPanel = openSearchPanel;
    window.openMapPanel = openMapPanel;
    window.openNotificationPanel = openNotificationPanel;
    window.searchFor = searchFor;
    window.toggleSearch = toggleSearch;
});

function initializePanels() {
    // Add panel overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-panel-overlay';
    overlay.id = 'panel-overlay';
    document.body.appendChild(overlay);
    
    // Close panels when clicking overlay
    overlay.addEventListener('click', function() {
        closeAllPanels();
    });
    
    // Close search panel when clicking outside
    document.addEventListener('click', function(e) {
        const searchPanel = document.getElementById('search-panel');
        const searchIcon = document.getElementById('search-icon');
        
        if (searchPanel && searchPanel.classList.contains('active')) {
            if (!searchPanel.contains(e.target) && !searchIcon.contains(e.target)) {
                closeAllPanels();
            }
        }
    });
    
    // Close panels with ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllPanels();
        }
    });
}

// Panel control functions
function openPanel(panelId) {
    closeAllPanels();
    
    const panel = document.getElementById(panelId);
    const overlay = document.getElementById('panel-overlay');
    
    if (panel && overlay) {
        panel.classList.add('active');
        overlay.classList.add('active');
        currentPanel = panelId;
        document.body.style.overflow = 'hidden';
        
        // Reinitialize search if search panel is opened
        if (panelId === 'search-panel') {
            initializeSearch();
            // Focus the search input but don't clear it
            const searchInput = document.getElementById('search-input-field');
            if (searchInput) {
                searchInput.focus();
            }
            
            // Also attach click listener to search button as fallback
            const searchButton = panel.querySelector('.modal-search-btn');
            if (searchButton) {
                searchButton.onclick = function() {
                    console.log('Search button clicked');
                    performSearch();
                };
            }
        }
    }
}

function closeAllPanels() {
    const panels = ['search-panel', 'map-panel', 'notification-panel'];
    const overlay = document.getElementById('panel-overlay');
    
    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.classList.remove('active');
        }
    });
    
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    currentPanel = null;
    document.body.style.overflow = '';
}

// Specific panel functions
function closeSearchPanel() {
    const panel = document.getElementById('search-panel');
    const overlay = document.getElementById('panel-overlay');
    
    if (panel) panel.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    
    currentPanel = null;
    document.body.style.overflow = '';
}

function closeMapPanel() {
    const panel = document.getElementById('map-panel');
    const overlay = document.getElementById('panel-overlay');
    
    if (panel) panel.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    
    currentPanel = null;
    document.body.style.overflow = '';
}

function closeNotificationPanel() {
    const panel = document.getElementById('notification-panel');
    const overlay = document.getElementById('panel-overlay');
    
    if (panel) panel.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    
    currentPanel = null;
    document.body.style.overflow = '';
}

// Search functionality
function initializeSearch() {
    // Wait a bit for the DOM to be ready
    setTimeout(() => {
        const searchInput = document.getElementById('search-input-field');
        if (searchInput) {
            console.log('Search input found:', searchInput);
            // Remove any existing listeners first
            searchInput.removeEventListener('keypress', handleSearchKeypress);
            // Add the event listener
            searchInput.addEventListener('keypress', handleSearchKeypress);
        } else {
            console.log('Search input not found!');
        }
        
        // Load recent searches from localStorage
        loadRecentSearches();
    }, 100);
}

function handleSearchKeypress(e) {
    console.log('Key pressed:', e.key);
    if (e.key === 'Enter') {
        console.log('Enter key pressed, calling performSearch');
        performSearch();
    }
}

function performSearch() {
    const searchInput = document.getElementById('search-input-field');
    const searchTerm = searchInput ? searchInput.value.trim() : '';
    
    console.log('performSearch called');
    console.log('searchInput element:', searchInput);
    console.log('searchTerm:', searchTerm);
    
    if (searchTerm) {
        console.log('Searching for:', searchTerm);
        
        // Call our search API to update weather location
        updateWeatherLocation(searchTerm);
    } else {
        console.log('No search term provided');
    }
}

async function updateWeatherLocation(searchTerm) {
    try {
        // Determine if we're in public or authenticated mode
        const isPublic = window.location.pathname.includes('/public');
        const apiEndpoint = isPublic ? '/api/search/public' : '/api/search';
        
        console.log('updateWeatherLocation called with:', searchTerm);
        console.log('isPublic:', isPublic);
        console.log('apiEndpoint:', apiEndpoint);
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_term: searchTerm
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success) {
            // Just reload the page immediately
            location.reload();
        } else {
            console.error('Search failed:', data.error);
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

function showSearchLoading() {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Updating weather location to: ${document.getElementById('search-input-field').value}</p>
            </div>
        `;
    }
}

function showSearchSuccess(message) {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="search-success">
                <i class="fas fa-check-circle text-success"></i>
                <h5>Success!</h5>
                <p>${message}</p>
                <p class="text-muted">Page will reload in a moment...</p>
            </div>
        `;
    }
}

function showSearchError(errorMessage) {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-triangle text-warning"></i>
                <h5>Search Error</h5>
                <p>${errorMessage}</p>
                <button class="btn btn-primary btn-sm" onclick="performSearch()">Try Again</button>
            </div>
        `;
    }
}

function searchFor(term) {
    const searchInput = document.getElementById('search-input-field');
    if (searchInput) {
        searchInput.value = term;
        performSearch();
    }
}

function showSearchResults(term) {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="search-results-content">
                <h4>Search Results for "${term}"</h4>
                <div class="result-item">
                    <h5>Location: ${term}</h5>
                    <p>Weather data and flood risk information for ${term}</p>
                    <button class="view-details-btn" onclick="viewLocationDetails('${term}')">
                        View Details
                    </button>
                </div>
            </div>
        `;
    }
}

function addToRecentSearches(term) {
    let recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    
    // Remove if already exists
    recentSearches = recentSearches.filter(item => item !== term);
    
    // Add to beginning
    recentSearches.unshift(term);
    
    // Keep only last 5
    recentSearches = recentSearches.slice(0, 5);
    
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches));
    loadRecentSearches();
}

function loadRecentSearches() {
    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    const recentList = document.getElementById('recent-searches-list');
    
    if (recentList) {
        if (recentSearches.length > 0) {
            recentList.innerHTML = recentSearches.map(term => 
                `<div class="recent-item" onclick="searchFor('${term}')">${term}</div>`
            ).join('');
        } else {
            recentList.innerHTML = '<div class="no-recent">No recent searches</div>';
        }
    }
}

function viewLocationDetails(location) {
    console.log('Viewing details for:', location);
    // Implement location details view
}

// Map functionality
function centerMap() {
    console.log('Centering map...');
    // Implement map centering
}

function toggleLayers() {
    console.log('Toggling map layers...');
    // Implement layer toggling
}

// Notification functionality
function initializeNotifications() {
    updateNotificationCount();
}

function filterNotifications(type) {
    const notifications = document.querySelectorAll('.notification-item');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    // Update active filter button
    filterBtns.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filter notifications
    notifications.forEach(notification => {
        if (type === 'all' || notification.classList.contains(type)) {
            notification.style.display = 'flex';
        } else {
            notification.style.display = 'none';
        }
    });
}

function markAsRead(button) {
    const notification = button.closest('.notification-item');
    if (notification) {
        notification.style.opacity = '0.5';
        button.style.display = 'none';
        updateNotificationCount();
    }
}

function markAllAsRead() {
    const notifications = document.querySelectorAll('.notification-item');
    const actionBtns = document.querySelectorAll('.action-btn');
    
    notifications.forEach(notification => {
        notification.style.opacity = '0.5';
    });
    
    actionBtns.forEach(btn => {
        btn.style.display = 'none';
    });
    
    updateNotificationCount();
}

function clearAllNotifications() {
    const notificationsList = document.getElementById('notifications-list');
    if (notificationsList) {
        notificationsList.innerHTML = '<div class="no-notifications">No notifications</div>';
        updateNotificationCount();
    }
}

function updateNotificationCount() {
    const unreadNotifications = document.querySelectorAll('.notification-item:not([style*="opacity: 0.5"])');
    const countElement = document.getElementById('notification-count');
    
    if (countElement) {
        countElement.textContent = unreadNotifications.length;
    }
}

// Global functions for navbar integration
function openSearchPanel() {
    openPanel('search-panel');
}

function toggleSearch() {
    openSearchPanel();
}

function openMapPanel() {
    openPanel('map-panel');
}

function openNotificationPanel() {
    openPanel('notification-panel');
}

