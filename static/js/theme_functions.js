// Theme Functions for Hotel Management System

// Carousel navigation
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.palette-carousel');
    const prevBtn = document.getElementById('palette-prev');
    const nextBtn = document.getElementById('palette-next');
    
    if (carousel && prevBtn && nextBtn) {
        const paletteItems = document.querySelectorAll('.palette-item');
        if (paletteItems.length > 0) {
            const itemWidth = paletteItems[0].offsetWidth + 30; // Width + margin/padding
            
            prevBtn.addEventListener('click', function() {
                carousel.scrollBy({left: -itemWidth * 4, behavior: 'smooth'});
            });
            
            nextBtn.addEventListener('click', function() {
                carousel.scrollBy({left: itemWidth * 4, behavior: 'smooth'});
            });
        }
    }

    // Update preview when color changes
    const colorInputs = document.querySelectorAll('.color-picker');
    colorInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Update the color preview
            const preview = this.parentElement.querySelector('.color-preview');
            if (preview) {
                preview.style.backgroundColor = this.value;
            }
            
            // Update the theme preview
            updateThemePreview();
            
            // Apply changes to the current page for real-time preview
            applyThemeChanges();
        });
    });
    
    // Reset button
    const resetBtn = document.getElementById('resetTheme');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Reset to default values
            document.querySelector('[name="primary_color"]').value = '#4285F4';
            document.querySelector('[name="secondary_color"]').value = '#34A853';
            document.querySelector('[name="danger_color"]').value = '#EA4335';
            document.querySelector('[name="warning_color"]').value = '#FBBC05';
            document.querySelector('[name="sidebar_color"]').value = '#343a40';
            
            // Update previews
            colorInputs.forEach(input => {
                const preview = input.parentElement.querySelector('.color-preview');
                if (preview) {
                    preview.style.backgroundColor = input.value;
                }
            });
            
            // Update theme preview and apply changes
            updateThemePreview();
            applyThemeChanges();
        });
    }
    
    // Palette preset buttons
    const paletteButtons = document.querySelectorAll('.apply-palette');
    paletteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const palette = this.dataset.palette;
            
            // Set colors based on the selected palette
            if (palette === 'neutral') {
                document.querySelector('[name="primary_color"]').value = '#D3CAC1';
                document.querySelector('[name="secondary_color"]').value = '#F6EEE0';
                document.querySelector('[name="danger_color"]').value = '#E6CCBE';
                document.querySelector('[name="warning_color"]').value = '#EAEAEA';
                document.querySelector('[name="sidebar_color"]').value = '#EAEAEA';
            } else if (palette === 'vibrant') {
                document.querySelector('[name="primary_color"]').value = '#4F8CB6';
                document.querySelector('[name="secondary_color"]').value = '#9DD9D2';
                document.querySelector('[name="danger_color"]').value = '#E94B4F';
                document.querySelector('[name="warning_color"]').value = '#F1F7ED';
                document.querySelector('[name="sidebar_color"]').value = '#254465';
            } else if (palette === 'earthy') {
                document.querySelector('[name="primary_color"]').value = '#9C8C8C';
                document.querySelector('[name="secondary_color"]').value = '#E6BFB2';
                document.querySelector('[name="danger_color"]').value = '#4A3F35';
                document.querySelector('[name="warning_color"]').value = '#D7D0C8';
                document.querySelector('[name="sidebar_color"]').value = '#4A3F35';
            } else if (palette === 'cool') {
                document.querySelector('[name="primary_color"]').value = '#475BE8';
                document.querySelector('[name="secondary_color"]').value = '#6B7CE0';
                document.querySelector('[name="danger_color"]').value = '#A8B6FF';
                document.querySelector('[name="warning_color"]').value = '#E6EFFF';
                document.querySelector('[name="sidebar_color"]').value = '#475BE8';
            } else if (palette === 'bright') {
                document.querySelector('[name="primary_color"]').value = '#1B4D73';
                document.querySelector('[name="secondary_color"]').value = '#06D6A0';
                document.querySelector('[name="danger_color"]').value = '#FB5B7F';
                document.querySelector('[name="warning_color"]').value = '#FFD166';
                document.querySelector('[name="sidebar_color"]').value = '#1B4D73';
            } else if (palette === 'contrast') {
                document.querySelector('[name="primary_color"]').value = '#1A3A8F';
                document.querySelector('[name="secondary_color"]').value = '#F9DB43';
                document.querySelector('[name="danger_color"]').value = '#E83D76';
                document.querySelector('[name="warning_color"]').value = '#F6F7EB';
                document.querySelector('[name="sidebar_color"]').value = '#373E40';
            } else if (palette === 'autumn') {
                document.querySelector('[name="primary_color"]').value = '#253C5B';
                document.querySelector('[name="secondary_color"]').value = '#F1883B';
                document.querySelector('[name="danger_color"]').value = '#6A1B1F';
                document.querySelector('[name="warning_color"]').value = '#D5D5D5';
                document.querySelector('[name="sidebar_color"]').value = '#0A6E47';
            } else if (palette === 'freshMint') {
                document.querySelector('[name="primary_color"]').value = '#85C7F8';
                document.querySelector('[name="secondary_color"]').value = '#5EFFC9';
                document.querySelector('[name="danger_color"]').value = '#8A7BC8';
                document.querySelector('[name="warning_color"]').value = '#FFFFFF';
                document.querySelector('[name="sidebar_color"]').value = '#000000';
            } else if (palette === 'ocean') {
                document.querySelector('[name="primary_color"]').value = '#1C64A5';
                document.querySelector('[name="secondary_color"]').value = '#77C0CE';
                document.querySelector('[name="danger_color"]').value = '#EA914E';
                document.querySelector('[name="warning_color"]').value = '#FFDD63';
                document.querySelector('[name="sidebar_color"]').value = '#53A7DA';
            }
            
            // Update previews
            colorInputs.forEach(input => {
                const preview = input.parentElement.querySelector('.color-preview');
                if (preview) {
                    preview.style.backgroundColor = input.value;
                }
            });
            
            // Update theme preview and apply changes
            updateThemePreview();
            applyThemeChanges();
        });
    });
    
    // Initial update of the theme preview
    setTimeout(() => {
        if (typeof updateThemePreview === 'function') {
            updateThemePreview();
        }
    }, 100);
});

// Update preview panel with current theme colors
function updateThemePreview() {
    const primaryColor = document.querySelector('[name="primary_color"]').value;
    const secondaryColor = document.querySelector('[name="secondary_color"]').value;
    const dangerColor = document.querySelector('[name="danger_color"]').value;
    const warningColor = document.querySelector('[name="warning_color"]').value;
    const sidebarColor = document.querySelector('[name="sidebar_color"]').value;
    
    // Update preview header
    document.querySelector('.preview-header').style.backgroundColor = primaryColor;
    
    // Update preview buttons
    document.querySelectorAll('.preview-buttons .btn')[0].style.backgroundColor = primaryColor;
    document.querySelectorAll('.preview-buttons .btn')[1].style.backgroundColor = secondaryColor;
    document.querySelectorAll('.preview-buttons .btn')[2].style.backgroundColor = dangerColor;
    document.querySelectorAll('.preview-buttons .btn')[3].style.backgroundColor = warningColor;
    
    // Update preview sidebar
    document.querySelector('.preview-sidebar').style.backgroundColor = sidebarColor;
}

// Apply theme changes to the actual page elements
function applyThemeChanges() {
    const primaryColor = document.querySelector('[name="primary_color"]').value;
    const secondaryColor = document.querySelector('[name="secondary_color"]').value;
    const dangerColor = document.querySelector('[name="danger_color"]').value;
    const warningColor = document.querySelector('[name="warning_color"]').value;
    const sidebarColor = document.querySelector('[name="sidebar_color"]').value;
    
    // Create a hidden form field to store theme settings
    let themeInput = document.getElementById('theme-settings-input');
    if (!themeInput) {
        themeInput = document.createElement('input');
        themeInput.type = 'hidden';
        themeInput.name = 'theme_settings';
        themeInput.id = 'theme-settings-input';
        const themeForm = document.getElementById('theme-form');
        if (themeForm) {
            themeForm.appendChild(themeInput);
        }
    }
    
    // Store theme settings as JSON
    const themeSettings = {
        primaryColor: primaryColor,
        secondaryColor: secondaryColor,
        dangerColor: dangerColor,
        warningColor: warningColor,
        sidebarColor: sidebarColor
    };
    
    if (themeInput) {
        themeInput.value = JSON.stringify(themeSettings);
    }
    
    // Save theme settings to localStorage for use across pages
    localStorage.setItem('theme_settings', JSON.stringify(themeSettings));
    
    // Apply theme colors to CSS variables for immediate visual update
    document.documentElement.style.setProperty('--primary-color', primaryColor);
    document.documentElement.style.setProperty('--secondary-color', secondaryColor);
    document.documentElement.style.setProperty('--danger-color', dangerColor);
    document.documentElement.style.setProperty('--warning-color', warningColor);
    document.documentElement.style.setProperty('--sidebar-color', sidebarColor);
    
    // Apply styles directly to elements
    // Sidebar
    document.querySelectorAll('.sidebar').forEach(el => {
        el.style.backgroundColor = sidebarColor;
    });
    
    document.querySelectorAll('.sidebar .logo').forEach(el => {
        el.style.backgroundColor = adjustColor(sidebarColor, -20);
    });
    
    // Active sidebar items
    document.querySelectorAll('.sidebar .nav-item.active').forEach(el => {
        el.style.backgroundColor = primaryColor;
        el.style.borderLeftColor = secondaryColor;
    });
    
    // All nav links should transition smoothly
    document.querySelectorAll('.sidebar .nav-item').forEach(item => {
        item.style.transition = 'all 0.3s ease';
    });
    
    // Hover effect for nav items
    const styleElement = document.getElementById('dynamic-sidebar-styles');
    if (!styleElement) {
        const newStyleElement = document.createElement('style');
        newStyleElement.id = 'dynamic-sidebar-styles';
        document.head.appendChild(newStyleElement);
        
        // Add CSS rules for hover states with the current theme colors
        newStyleElement.textContent = `
            .sidebar .nav-item:hover {
                background-color: ${adjustColor(sidebarColor, 10)};
            }
            .sidebar .nav-item.active:hover {
                background-color: ${adjustColor(primaryColor, 10)};
            }
        `;
    } else {
        // Update existing style element
        styleElement.textContent = `
            .sidebar .nav-item:hover {
                background-color: ${adjustColor(sidebarColor, 10)};
            }
            .sidebar .nav-item.active:hover {
                background-color: ${adjustColor(primaryColor, 10)};
            }
        `;
    }
    
    // Buttons
    document.querySelectorAll('.btn-primary').forEach(el => {
        el.style.backgroundColor = primaryColor;
        el.style.borderColor = primaryColor;
    });
    
    document.querySelectorAll('.btn-secondary').forEach(el => {
        el.style.backgroundColor = secondaryColor;
        el.style.borderColor = secondaryColor;
    });
    
    document.querySelectorAll('.btn-danger').forEach(el => {
        el.style.backgroundColor = dangerColor;
        el.style.borderColor = dangerColor;
    });
    
    document.querySelectorAll('.btn-warning').forEach(el => {
        el.style.backgroundColor = warningColor;
        el.style.borderColor = warningColor;
    });
    
    // Stats cards
    document.querySelectorAll('.stats-card.blue').forEach(el => {
        el.style.borderLeftColor = primaryColor;
    });
    
    document.querySelectorAll('.stats-card.green').forEach(el => {
        el.style.borderLeftColor = secondaryColor;
    });
    
    document.querySelectorAll('.stats-card.yellow').forEach(el => {
        el.style.borderLeftColor = warningColor;
    });
    
    document.querySelectorAll('.stats-card.red').forEach(el => {
        el.style.borderLeftColor = dangerColor;
    });
    
    // Quick access icons
    document.querySelectorAll('.quick-access-card.blue .icon').forEach(el => {
        el.style.color = primaryColor;
    });
    
    document.querySelectorAll('.quick-access-card.green .icon').forEach(el => {
        el.style.color = secondaryColor;
    });
    
    // Active nav links
    document.querySelectorAll('.nav-link.active').forEach(el => {
        el.style.backgroundColor = adjustColor(sidebarColor, 15);
    });
}

// Helper function to darken/lighten colors
function adjustColor(color, amount) {
    return '#' + color.replace(/^#/, '').replace(/../g, colorHex => 
        ('0' + Math.min(255, Math.max(0, parseInt(colorHex, 16) + amount)).toString(16)).slice(-2)
    );
} 