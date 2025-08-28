document.addEventListener("DOMContentLoaded", function() {
    // iOS-style cubic easing
    function iosEasing(t) {
        return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3)/2;
    }

    // Smooth scroll without Lenis
    function smoothScroll(target, duration = 1200, easingFunc = iosEasing) {
        const start = window.scrollY;
        const end = target.getBoundingClientRect().top + start;
        const startTime = performance.now();

        function scroll() {
            const now = performance.now();
            const time = Math.min(1, (now - startTime) / duration);
            const eased = easingFunc(time);
            window.scrollTo(0, start + (end - start) * eased);
            if(time < 1) requestAnimationFrame(scroll);
        }
        requestAnimationFrame(scroll);
    }

    // Anchor smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if(target) smoothScroll(target, 1200);
        });
    });

    // Navbar shadow on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if(navbar) {
            if(window.scrollY > 50) navbar.classList.add('navbar-scrolled');
            else navbar.classList.remove('navbar-scrolled');
        }
    });

    // Section fade-in on scroll
    const sections = document.querySelectorAll('.scroll-section');
    function checkSections() {
        const scrollTop = window.scrollY || window.pageYOffset;
        sections.forEach(section => {
            if(section.offsetTop < scrollTop + window.innerHeight - 100){
                section.classList.add('active');
            }
        });
    }
    window.addEventListener('scroll', checkSections);
    checkSections();
});
