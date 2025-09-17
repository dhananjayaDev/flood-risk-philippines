// UI Utilities Module

// Update datetime
function updateDateTime() {
    const now = new Date();
    const options = { 
        day: '2-digit', 
        month: 'short', 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    };
    const dateTimeString = now.toLocaleDateString('en-GB', options).replace(',', ' |');
    document.getElementById('current-datetime').textContent = dateTimeString;
}

// Dropdown functionality
function initDropdown() {
    const userDropdown = document.querySelector('.user-dropdown');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (userDropdown && dropdownMenu) {
        let isOpen = false;
        
        // Toggle dropdown on click
        userDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Dropdown clicked, current state:', isOpen);
            isOpen = !isOpen;
            
            if (isOpen) {
                dropdownMenu.classList.add('show');
                console.log('Dropdown opened');
            } else {
                dropdownMenu.classList.remove('show');
                console.log('Dropdown closed');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target) && isOpen) {
                isOpen = false;
                dropdownMenu.classList.remove('show');
            }
        });
        
        // Prevent dropdown from closing when clicking inside it
        dropdownMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}

// Fix layout for high-resolution laptops
function fixHighResLayout() {
    const screenWidth = window.screen.width;
    const screenHeight = window.screen.height;
    
    if (screenWidth >= 2000) {
        document.body.classList.add('high-res-layout');
    }
    
    // Specific fix for MSI Cyborg 16 A12V
    if (screenWidth === 2560 && screenHeight === 1600) {
        document.body.classList.add('msi-cyborg-layout');
    }
}

// Search bar functionality
function initSearchBar() {
    const searchIcon = document.getElementById('search-icon');
    const searchBar = document.getElementById('floating-search-bar');
    const searchInput = document.getElementById('search-input');
    
    if (!searchIcon || !searchBar || !searchInput) {
        console.log('Search elements not found');
        return;
    }
    
    let isSearchOpen = false;
    
    // Open search bar
    searchIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Search icon clicked');
        
        if (!isSearchOpen) {
            searchBar.classList.add('show');
            isSearchOpen = true;
            
            // Focus on input after animation
            setTimeout(() => {
                searchInput.focus();
            }, 300);
        }
    });
    
    // Close search bar
    function closeSearch() {
        if (isSearchOpen) {
            searchBar.classList.remove('show');
            isSearchOpen = false;
            searchInput.value = '';
        }
    }
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isSearchOpen) {
            closeSearch();
        }
    });
    
    // Close when clicking outside
    document.addEventListener('click', function(e) {
        if (isSearchOpen && !searchBar.contains(e.target) && !searchIcon.contains(e.target)) {
            closeSearch();
        }
    });
    
    // Handle Enter key in search
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                console.log('Searching for:', query);
                // Here you can add actual search functionality
                closeSearch();
            }
        }
    });
}

// Map panel functionality
function initMapPanel() {
    const mapIcon = document.getElementById('map-icon');
    const mapPanel = document.getElementById('map-panel');
    const mapClose = document.getElementById('map-close');
    const backgroundOverlay = document.getElementById('background-overlay');
    
    if (!mapIcon || !mapPanel || !mapClose || !backgroundOverlay) {
        console.log('Map elements not found');
        return;
    }
    
    let isMapOpen = false;
    
    // Open map panel
    mapIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Map icon clicked');
        
        if (!isMapOpen) {
            mapPanel.classList.add('show');
            backgroundOverlay.classList.add('show');
            isMapOpen = true;
            
            // Prevent body scroll when map is open
            document.body.style.overflow = 'hidden';
        }
    });
    
    // Close map panel
    function closeMap() {
        if (isMapOpen) {
            mapPanel.classList.remove('show');
            backgroundOverlay.classList.remove('show');
            isMapOpen = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    }
    
    mapClose.addEventListener('click', closeMap);
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMapOpen) {
            closeMap();
        }
    });
    
    // Close when clicking on background overlay
    backgroundOverlay.addEventListener('click', closeMap);
    
    // Close when clicking outside map panel
    document.addEventListener('click', function(e) {
        if (isMapOpen && !mapPanel.contains(e.target) && !mapIcon.contains(e.target)) {
            closeMap();
        }
    });
    
    // Handle map loading
    const mapIframe = document.getElementById('map-iframe');
    
    if (mapIframe) {
        mapIframe.addEventListener('load', function() {
            console.log('Map loaded successfully');
        });
    }
    
    // Handle map control buttons
    const currentLocationBtn = document.getElementById('current-location-btn');
    const riskLayersBtn = document.getElementById('risk-layers-btn');
    const zoomInBtn = document.getElementById('zoom-in-btn');
    
    if (currentLocationBtn) {
        currentLocationBtn.addEventListener('click', function() {
            console.log('Current Location clicked');
            // Get user's current location and update map
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const newSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${lng-0.1},${lat-0.1},${lng+0.1},${lat+0.1}&layer=mapnik&marker=${lat},${lng}`;
                    mapIframe.src = newSrc;
                });
            } else {
                alert('Geolocation is not supported by this browser.');
            }
        });
    }
    
    if (riskLayersBtn) {
        riskLayersBtn.addEventListener('click', function() {
            console.log('Risk Layers clicked');
            // Toggle risk layer visibility
            alert('Risk layers feature - Coming soon!');
        });
    }
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', function() {
            console.log('Zoom In clicked');
            // Zoom in functionality
            alert('Zoom in feature - Coming soon!');
        });
    }
}

// Notifications panel functionality
function initNotificationsPanel() {
    const notificationIcon = document.getElementById('notification-icon');
    const notificationsPanel = document.getElementById('notifications-panel');
    const notificationsClose = document.getElementById('notifications-close');
    const backgroundOverlay = document.getElementById('background-overlay');
    
    console.log('Initializing notifications panel...');
    console.log('Notification icon found:', !!notificationIcon);
    console.log('Notifications panel found:', !!notificationsPanel);
    console.log('Notifications close found:', !!notificationsClose);
    console.log('Background overlay found:', !!backgroundOverlay);
    
    if (!notificationIcon || !notificationsPanel || !notificationsClose || !backgroundOverlay) {
        console.log('Notification elements not found');
        return;
    }
    
    let isNotificationsOpen = false;
    
    // Open notifications panel
    notificationIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Notification icon clicked');
        
        if (!isNotificationsOpen) {
            notificationsPanel.classList.add('show');
            backgroundOverlay.classList.add('show');
            isNotificationsOpen = true;
            
            // Prevent body scroll when notifications are open
            document.body.style.overflow = 'hidden';
        }
    });
    
    // Close notifications panel
    function closeNotifications() {
        if (isNotificationsOpen) {
            notificationsPanel.classList.remove('show');
            backgroundOverlay.classList.remove('show');
            isNotificationsOpen = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    }
    
    notificationsClose.addEventListener('click', closeNotifications);
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isNotificationsOpen) {
            closeNotifications();
        }
    });
    
    // Close when clicking on background overlay
    backgroundOverlay.addEventListener('click', closeNotifications);
    
    // Close when clicking outside notifications panel
    document.addEventListener('click', function(e) {
        if (isNotificationsOpen && !notificationsPanel.contains(e.target) && !notificationIcon.contains(e.target)) {
            closeNotifications();
        }
    });
    
    // Handle notification item clicks
    const notificationItems = document.querySelectorAll('.notification-item');
    const notificationBadge = document.getElementById('notification-badge');
    
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            notificationItems.forEach(ni => ni.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');
            
            const title = this.querySelector('.notification-title').textContent;
            console.log('Notification clicked:', title);
        });
    });
    
    // Update notification badge count
    function updateNotificationBadge() {
        if (notificationBadge) {
            const activeNotifications = document.querySelectorAll('.notification-item:not(.read)').length;
            notificationBadge.textContent = activeNotifications;
            notificationBadge.style.display = activeNotifications > 0 ? 'flex' : 'none';
        }
    }
    
    // Initialize badge count
    updateNotificationBadge();
}

// Initialize all UI components
function initSettingsPanel() {
    const settingsDropdownItem = document.getElementById('settings-dropdown-item');
    const settingsPanel = document.getElementById('settings-panel');
    const settingsClose = document.getElementById('settings-close');
    const backgroundOverlay = document.getElementById('background-overlay');
    
    console.log('Initializing settings panel...');
    console.log('Settings dropdown item found:', !!settingsDropdownItem);
    console.log('Settings panel found:', !!settingsPanel);
    console.log('Settings close found:', !!settingsClose);
    console.log('Background overlay found:', !!backgroundOverlay);
    
    if (!settingsDropdownItem || !settingsPanel || !settingsClose || !backgroundOverlay) {
        console.log('Settings elements not found');
        return;
    }
    
    let isSettingsOpen = false;
    
    // Open settings panel
    settingsDropdownItem.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Settings dropdown item clicked');
        
        if (!isSettingsOpen) {
            settingsPanel.classList.add('show');
            backgroundOverlay.classList.add('show');
            isSettingsOpen = true;
            
            // Prevent body scroll when settings are open
            document.body.style.overflow = 'hidden';
            
            // Close the dropdown menu
            const dropdownMenu = document.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                dropdownMenu.classList.remove('show');
            }
        }
    });
    
    // Close settings panel
    function closeSettings() {
        if (isSettingsOpen) {
            settingsPanel.classList.remove('show');
            backgroundOverlay.classList.remove('show');
            isSettingsOpen = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    }
    
    settingsClose.addEventListener('click', closeSettings);
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isSettingsOpen) {
            closeSettings();
        }
    });
    
    // Close when clicking on background overlay
    backgroundOverlay.addEventListener('click', closeSettings);
    
    // Close when clicking outside settings panel
    document.addEventListener('click', function(e) {
        if (isSettingsOpen && !settingsPanel.contains(e.target) && !settingsDropdownItem.contains(e.target)) {
            closeSettings();
        }
    });
    
    // Handle settings form interactions
    const saveBtn = document.querySelector('.settings-btn-primary');
    const logoutBtn = document.querySelector('.settings-btn-danger');
    const changePasswordBtn = document.querySelector('.settings-btn-secondary');
    
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            console.log('Save settings clicked');
            // Here you can add actual save functionality
            closeSettings();
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            console.log('Logout clicked');
            // Redirect to logout
            window.location.href = '/auth/logout';
        });
    }
    
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function() {
            console.log('Change password clicked');
            // Here you can add change password functionality
        });
    }
    
    // Handle toggle switches
    const toggles = document.querySelectorAll('.settings-toggle input[type="checkbox"]');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            console.log('Toggle changed:', this.id, this.checked);
            // Here you can add toggle functionality
        });
    });
    
    // Handle select changes
    const selects = document.querySelectorAll('.settings-select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            console.log('Select changed:', this.name || this.id, this.value);
            // Here you can add select functionality
        });
    });
}

function initUI() {
    updateDateTime();
    initDropdown();
    initSearchBar();
    initMapPanel();
    initNotificationsPanel();
    initSettingsPanel();
    fixHighResLayout();
    
    // Run on window resize
    window.addEventListener('resize', fixHighResLayout);
    
    // Update datetime every minute
    setInterval(updateDateTime, 60000);
}
