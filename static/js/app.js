/**
 * Main JavaScript file for PWA functionality
 * Handles service worker registration, API calls, and UI interactions
 */

// ============================================
// Service Worker Registration
// ============================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered successfully:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// ============================================
// Navigation Drawer Functions
// ============================================

const menuBtn = document.getElementById('menuBtn');
const navDrawer = document.getElementById('navDrawer');
const overlay = document.getElementById('overlay');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        navDrawer.classList.add('active');
        overlay.classList.add('active');
    });
}

if (overlay) {
    overlay.addEventListener('click', () => {
        navDrawer.classList.remove('active');
        overlay.classList.remove('active');
        // Also close user menu if open
        const userMenu = document.getElementById('userMenu');
        if (userMenu) {
            userMenu.style.display = 'none';
        }
    });
}

// ============================================
// User Menu Toggle
// ============================================

const moreBtn = document.getElementById('moreBtn');
const userMenu = document.getElementById('userMenu');

if (moreBtn && userMenu) {
    moreBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = userMenu.style.display === 'block';
        userMenu.style.display = isVisible ? 'none' : 'block';
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (userMenu && !userMenu.contains(e.target) && e.target !== moreBtn) {
            userMenu.style.display = 'none';
        }
    });
}

// ============================================
// Snackbar (Toast Notification)
// ============================================

function showSnackbar(message) {
    const snackbar = document.getElementById('snackbar');
    snackbar.textContent = message;
    snackbar.classList.add('active');
    
    setTimeout(() => {
        snackbar.classList.remove('active');
    }, 3000);
}

// ============================================
// Check In Dialog Functions
// ============================================

function showCheckInDialog() {
    const dialog = document.getElementById('checkInDialog');
    if (dialog) {
        dialog.classList.add('active');
    }
}

function hideCheckInDialog() {
    const dialog = document.getElementById('checkInDialog');
    if (dialog) {
        dialog.classList.remove('active');
    }
}

// Handle Check In Form Submission
const checkInForm = document.getElementById('checkInForm');
if (checkInForm) {
    checkInForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userId = document.getElementById('checkInUserId').value;
        const notes = document.getElementById('checkInNotes').value;
        
        try {
            const response = await fetch('/api/attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: parseInt(userId),
                    notes: notes
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSnackbar('Check-in successful!');
                hideCheckInDialog();
                checkInForm.reset();
                // Reload page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showSnackbar('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            showSnackbar('Failed to check in. Please try again.');
        }
    });
}

// Quick check-in from user list
function checkInUser(userId, userName) {
    if (confirm(`Check in ${userName}?`)) {
        fetch('/api/attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                notes: ''
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSnackbar(`${userName} checked in successfully!`);
            } else {
                showSnackbar('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSnackbar('Failed to check in. Please try again.');
        });
    }
}

// ============================================
// Check Out Dialog Functions
// ============================================

function showCheckOutDialog() {
    showSnackbar('Please check out from the Attendance Records page');
}

// Handle check out
function checkOut(attendanceId) {
    if (confirm('Confirm check-out?')) {
        fetch(`/api/attendance/${attendanceId}/checkout`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSnackbar('Checked out successfully!');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showSnackbar('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSnackbar('Failed to check out. Please try again.');
        });
    }
}

// ============================================
// Add User Dialog Functions
// ============================================

function showAddUserDialog() {
    const dialog = document.getElementById('addUserDialog');
    if (dialog) {
        dialog.classList.add('active');
    }
}

function hideAddUserDialog() {
    const dialog = document.getElementById('addUserDialog');
    if (dialog) {
        dialog.classList.remove('active');
    }
}

// Handle Add User Form Submission
const addUserForm = document.getElementById('addUserForm');
if (addUserForm) {
    addUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('userName').value;
        const email = document.getElementById('userEmail').value;
        
        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    email: email
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSnackbar('User added successfully!');
                hideAddUserDialog();
                addUserForm.reset();
                // Reload page after a short delay
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showSnackbar('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            showSnackbar('Failed to add user. Please try again.');
        }
    });
}

// Handle Delete User
function deleteUser(userId, userName) {
    if (confirm(`Are you sure you want to delete ${userName}?`)) {
        fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSnackbar('User deleted successfully!');
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                showSnackbar('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSnackbar('Failed to delete user. Please try again.');
        });
    }
}

// ============================================
// PWA Install Prompt
// ============================================

let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    
    // Show install button or prompt
    console.log('PWA install prompt available');
    
    // You can show a custom install button here
    showInstallPromotion();
});

function showInstallPromotion() {
    // Show a banner or button to install the app
    // This is optional - browser will show its own prompt
    const installPrompt = document.createElement('div');
    installPrompt.style.cssText = `
        position: fixed;
        bottom: 72px;
        left: 16px;
        right: 16px;
        background: white;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 2000;
    `;
    
    installPrompt.innerHTML = `
        <span style="flex: 1;">Install this app for better experience!</span>
        <button id="installBtn" style="background: #6200ea; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: 500;">Install</button>
        <button id="dismissBtn" style="background: none; border: none; color: #666;">✕</button>
    `;
    
    document.body.appendChild(installPrompt);
    
    document.getElementById('installBtn').addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
            installPrompt.remove();
        }
    });
    
    document.getElementById('dismissBtn').addEventListener('click', () => {
        installPrompt.remove();
    });
}

window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    showSnackbar('App installed successfully!');
});

// ============================================
// Online/Offline Status
// ============================================

window.addEventListener('online', () => {
    showSnackbar('You are back online!');
});

window.addEventListener('offline', () => {
    showSnackbar('You are offline. Some features may not work.');
});

// ============================================
// Prevent Pull-to-Refresh on Mobile
// ============================================

let touchStartY = 0;
document.addEventListener('touchstart', (e) => {
    touchStartY = e.touches[0].clientY;
}, { passive: true });

document.addEventListener('touchmove', (e) => {
    const touchY = e.touches[0].clientY;
    const touchDiff = touchY - touchStartY;
    
    // Prevent pull-to-refresh if at the top and pulling down
    if (touchDiff > 0 && window.scrollY === 0) {
        e.preventDefault();
    }
}, { passive: false });
