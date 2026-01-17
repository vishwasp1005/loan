// ========================================
// 🔥 LOANSHIELD - PROFESSIONAL ANIMATIONS
// ========================================

// ==========================================
// 1. SMOOTH SCROLL REVEAL ANIMATIONS
// ==========================================
const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
};

const revealOnScroll = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }
    });
}, observerOptions);

// Observe all elements with scroll-reveal classes
document.addEventListener('DOMContentLoaded', () => {
    const scrollElements = document.querySelectorAll(
        '.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right'
    );
    scrollElements.forEach(el => revealOnScroll.observe(el));
    
    // Stagger animation for children
    const staggerParents = document.querySelectorAll('.stagger-parent');
    staggerParents.forEach(parent => {
        const children = parent.querySelectorAll('.stagger-child');
        children.forEach((child, index) => {
            setTimeout(() => {
                child.classList.add('active');
            }, index * 100); // 100ms delay between each
        });
    });
});

// ==========================================
// 2. NAVBAR SCROLL EFFECT
// ==========================================
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add scrolled class for styling
    if (currentScroll > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// ==========================================
// 3. MOBILE HAMBURGER MENU
// ==========================================
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('open');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            hamburger.classList.remove('open');
            navLinks.classList.remove('active');
        }
    });
    
    // Close menu when clicking a link
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            hamburger.classList.remove('open');
            navLinks.classList.remove('active');
        });
    });
}

// ==========================================
// 4. CARD TILT EFFECT (3D)
// ==========================================
const cards = document.querySelectorAll('.stat-card, .chart-box, .form-card');

cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 15;
        const rotateY = (centerX - x) / 15;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
    });
});

// ==========================================
// 5. SMOOTH NUMBER COUNTER ANIMATION
// ==========================================
const animateCounter = (element, target, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
};

// Trigger counters when in view
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
            const target = parseInt(entry.target.getAttribute('data-count'));
            animateCounter(entry.target, target);
            entry.target.classList.add('counted');
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-box h2, .stat-card h2').forEach(counter => {
    const text = counter.textContent;
    const numbers = text.match(/\d+/);
    if (numbers) {
        counter.setAttribute('data-count', numbers[0]);
        counter.textContent = '0';
        counterObserver.observe(counter);
    }
});

// ==========================================
// 6. RIPPLE EFFECT ON BUTTONS
// ==========================================
const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, button');

buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple-effect');
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    button, .btn-primary, .btn-secondary {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

// ==========================================
// 7. PARALLAX EFFECT ON IMAGES
// ==========================================
window.addEventListener('scroll', () => {
    const parallaxElements = document.querySelectorAll('.hero-image img, .predict-illustration img');
    const scrolled = window.pageYOffset;
    
    parallaxElements.forEach(el => {
        const speed = 0.5;
        el.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// ==========================================
// 8. FORM INPUT ANIMATIONS
// ==========================================
const inputs = document.querySelectorAll('input, textarea, select');

inputs.forEach(input => {
    // Focus animation
    input.addEventListener('focus', function() {
        this.parentElement.classList.add('input-focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement.classList.remove('input-focused');
        if (this.value) {
            this.parentElement.classList.add('input-filled');
        } else {
            this.parentElement.classList.remove('input-filled');
        }
    });
});

// ==========================================
// 9. PAGE LOAD ANIMATIONS
// ==========================================
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
     document.body.style.opacity = '1'; 
    
    // Animate elements in sequence
    const heroElements = document.querySelectorAll('.hero-text > *, .hero-image');
    heroElements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 150);
    });
});

// ==========================================
// 10. SMOOTH ANCHOR SCROLLING
// ==========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==========================================
// 11. LOADING SPINNER ENHANCEMENT
// ==========================================
if (document.querySelector('.loader-overlay')) {
    const loader = document.querySelector('.loader-overlay');
    
    // Add particle effect
    for (let i = 0; i < 8; i++) {
        const particle = document.createElement('div');
        particle.className = 'loader-particle';
        particle.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background: #C7A27C;
            border-radius: 50%;
            animation: particle-float ${1 + Math.random()}s ease-in-out infinite;
            animation-delay: ${i * 0.1}s;
        `;
        loader.querySelector('.loader')?.appendChild(particle);
    }
}

// ==========================================
// 12. TOAST NOTIFICATIONS (OPTIONAL)
// ==========================================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#C7A27C'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add toast CSS
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(toastStyle);

// ==========================================
// 13. CURSOR TRAIL EFFECT (OPTIONAL)
// ==========================================
const createCursorTrail = () => {
    let dots = [];
    const maxDots = 12;
    
    document.addEventListener('mousemove', (e) => {
        const dot = document.createElement('div');
        dot.className = 'cursor-dot';
        dot.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: rgba(199, 162, 124, 0.5);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            left: ${e.clientX - 4}px;
            top: ${e.clientY - 4}px;
            animation: dotFade 0.8s ease-out forwards;
        `;
        
        document.body.appendChild(dot);
        dots.push(dot);
        
        if (dots.length > maxDots) {
            dots[0].remove();
            dots.shift();
        }
        
        setTimeout(() => dot.remove(), 800);
    });
};

// Uncomment to enable cursor trail
// createCursorTrail();

const cursorStyle = document.createElement('style');
cursorStyle.textContent = `
    @keyframes dotFade {
        to {
            transform: scale(0);
            opacity: 0;
        }
    }
`;
document.head.appendChild(cursorStyle);

console.log('🔥 LoanShield Professional Animations Loaded!');

