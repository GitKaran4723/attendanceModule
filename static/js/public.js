/**
 * BCA BUB Public Pages JavaScript
 * Handles navigation, mobile menu, PWA installation, and animations
 */

// ============================================
// Navigation Scroll Effect
// ============================================
const initNavigation = () => {
    const navbar = document.getElementById('navbar');

    if (!navbar) return;

    const handleScroll = () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    // Initial check
    handleScroll();
};

// ============================================
// Mobile Menu
// ============================================
const initMobileMenu = () => {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuClose = document.getElementById('mobileMenuClose');

    if (!mobileMenuToggle || !mobileMenu) return;

    const openMenu = () => {
        mobileMenu.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    const closeMenu = () => {
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
    };

    mobileMenuToggle.addEventListener('click', openMenu);

    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMenu);
    }

    // Close menu when clicking a link
    document.querySelectorAll('.mobile-menu-links a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMenu();
        }
    });
};

// ============================================
// PWA Installation
// ============================================
let deferredPrompt = null;

const initPWAInstall = () => {
    const installPrompt = document.getElementById('installPrompt');
    const installBtn = document.getElementById('installBtn');
    const installClose = document.getElementById('installClose');

    if (!installPrompt) return;

    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        // Show install prompt after a delay
        setTimeout(() => {
            installPrompt.style.display = 'flex';
        }, 3000);
    });

    // Handle install button click
    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`PWA Install: ${outcome}`);
                deferredPrompt = null;
                installPrompt.style.display = 'none';
            }
        });
    }

    // Handle close button
    if (installClose) {
        installClose.addEventListener('click', () => {
            installPrompt.style.display = 'none';
        });
    }

    // Hide prompt if app is already installed
    window.addEventListener('appinstalled', () => {
        installPrompt.style.display = 'none';
        deferredPrompt = null;
        console.log('PWA installed successfully');
    });
};

// ============================================
// Service Worker Registration
// ============================================
const initServiceWorker = () => {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration.scope);
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        });
    }
};

// ============================================
// Smooth Scroll for Anchor Links
// ============================================
const initSmoothScroll = () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            const href = anchor.getAttribute('href');

            if (href === '#') return;

            e.preventDefault();

            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
};

// ============================================
// Animate Elements on Scroll
// ============================================
const initScrollAnimations = () => {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe cards and sections
    document.querySelectorAll('.feature-card, .team-card, .step-card, .timeline-item, .achievement-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
};

// Add CSS for animation
const addAnimationStyles = () => {
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
};

// ============================================
// Counter Animation for Stats
// ============================================
const animateCounter = (element, target, duration = 2000) => {
    let start = 0;
    const increment = target / (duration / 16);

    const updateCounter = () => {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start) + '+';
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target + '+';
        }
    };

    updateCounter();
};

const initCounterAnimation = () => {
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const target = parseInt(element.getAttribute('data-count'));

                if (target && !isNaN(target)) {
                    animateCounter(element, target);
                }

                statsObserver.unobserve(element);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-count]').forEach(el => {
        statsObserver.observe(el);
    });
};

// ============================================
// Utility Functions
// ============================================
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// ============================================
// Initialize All Functions
// ============================================
const init = () => {
    addAnimationStyles();
    initNavigation();
    initMobileMenu();
    initPWAInstall();
    initServiceWorker();
    initSmoothScroll();
    initScrollAnimations();
    initCounterAnimation();
};

// Run on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { init, initNavigation, initMobileMenu, initPWAInstall };
}
