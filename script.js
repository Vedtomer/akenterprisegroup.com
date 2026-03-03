/**
 * Main Script for Sunil Merchandising Premium Theme
 * GSAP, ScrollTrigger, Lenis, SwiperJS
 */

// Wait for DOM to load
document.addEventListener("DOMContentLoaded", () => {
    
    // --------------------------------------------------------
    // 1. Initialize Lenis (Smooth Scrolling)
    // --------------------------------------------------------
    const lenis = new window.Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
    });

    // Integrated Lenis with GSAP ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);

    gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);

    // --------------------------------------------------------
    // 2. Navbar Scroll Effect & Mobile Menu
    // --------------------------------------------------------
    const navbarInner = document.querySelector('.nav-inner-container');
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    let isMenuOpen = false;

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbarInner.classList.add('nav-scrolled');
            navbarInner.classList.remove('bg-transparent', 'py-3');
            navbarInner.classList.add('py-4');
        } else {
            navbarInner.classList.remove('nav-scrolled');
            navbarInner.classList.add('bg-transparent', 'py-3');
            navbarInner.classList.remove('py-4');
        }
    });

    // Mobile Menu Toggle
    mobileBtn.addEventListener('click', () => {
        isMenuOpen = !isMenuOpen;
        const spans = mobileBtn.querySelectorAll('span');
        
        if (isMenuOpen) {
            mobileMenu.classList.remove('translate-x-full');
            // Animate hamburger to X
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            spans.forEach(s => s.classList.add('bg-white'));
            
            // Animate links in
            gsap.fromTo(mobileLinks, 
                { y: 50, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.5, stagger: 0.1, delay: 0.2, ease: "power3.out" }
            );
        } else {
            mobileMenu.classList.add('translate-x-full');
            // Reset hamburger
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
            if (window.scrollY <= 50) {
                spans.forEach(s => s.classList.remove('bg-white'));
            }
        }
    });

    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileBtn.click(); // Close menu on click
        });
    });

    // --------------------------------------------------------
    // 3. Hero Section GSAP Animations
    // --------------------------------------------------------
    const heroTl = gsap.timeline();

    heroTl.to('.hero-title span', {
        y: 0,
        duration: 1.2,
        stagger: 0.2,
        ease: "power4.out",
        delay: 0.2
    })
    .to('.hero-subtitle', {
        y: 0,
        opacity: 1,
        duration: 1,
        ease: "power3.out"
    }, "-=1")
    .to('.hero-text', {
        opacity: 1,
        duration: 1,
        ease: "power2.out"
    }, "-=0.8")
    .to('.hero-cta', {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: "power2.out"
    }, "-=0.6");

    // Parallax Hero BG
    gsap.to('.hero-bg', {
        yPercent: 30,
        ease: "none",
        scrollTrigger: {
            trigger: "#home",
            start: "top top",
            end: "bottom top",
            scrub: true
        }
    });

    // --------------------------------------------------------
    // 4. About Section Animations
    // --------------------------------------------------------
    // Image Mask Reveal
    gsap.to('.about-img-mask', {
        scaleY: 0,
        duration: 1.5,
        ease: "power4.inOut",
        scrollTrigger: {
            trigger: "#about",
            start: "top 70%",
            end: "bottom top"
        }
    });

    // Image gentle zoom out
    gsap.to('.about-img', {
        scale: 1,
        duration: 2,
        ease: "power2.out",
        scrollTrigger: {
            trigger: "#about",
            start: "top 70%",
        }
    });

    // Text slide up stagger
    gsap.from('.about-content > *', {
        y: 50,
        opacity: 0,
        duration: 1,
        stagger: 0.15,
        ease: "power3.out",
        scrollTrigger: {
            trigger: "#about",
            start: "top 60%",
        }
    });

    // --------------------------------------------------------
    // 5. Services Cards Hover & Reveal
    // --------------------------------------------------------
    const serviceCards = document.querySelectorAll('.service-card');
    
    // Reveal
    gsap.from(serviceCards, {
        y: 100,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: "#services",
            start: "top 75%",
        }
    });
    
    gsap.from(['.services-subtitle', '.services-title'], {
        y: 40,
        opacity: 0,
        duration: 1,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: {
            trigger: "#services",
            start: "top 80%",
        }
    });

    // Magnetic 3D Tilt Effect
    serviceCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;

            gsap.to(card, {
                rotateX: rotateX,
                rotateY: rotateY,
                duration: 0.5,
                ease: "power2.out"
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                rotateX: 0,
                rotateY: 0,
                duration: 0.5,
                ease: "power2.out"
            });
        });
    });

    // --------------------------------------------------------
    // 6. Magnetic Buttons Universal
    // --------------------------------------------------------
    const magneticBtns = document.querySelectorAll('.magnetic-btn');
    
    magneticBtns.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            gsap.to(btn, {
                x: x * 0.3,
                y: y * 0.3,
                duration: 0.4,
                ease: "power2.out"
            });
            
            // Move text inside slightly more
            const txt = btn.querySelector('span');
            if(txt) {
                gsap.to(txt, {
                    x: x * 0.1,
                    y: y * 0.1,
                    duration: 0.4,
                    ease: "power2.out"
                });
            }
        });

        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                x: 0,
                y: 0,
                duration: 0.4,
                ease: "elastic.out(1, 0.3)"
            });
            
            const txt = btn.querySelector('span');
            if(txt) {
                gsap.to(txt, {
                    x: 0,
                    y: 0,
                    duration: 0.4,
                    ease: "elastic.out(1, 0.3)"
                });
            }
        });
    });

    // --------------------------------------------------------
    // 7. Swiper Slider (Product Showcase)
    // --------------------------------------------------------
    const mySwiper = new Swiper('.product-swiper', {
        effect: 'coverflow',
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',
        coverflowEffect: {
            rotate: 20,
            stretch: 0,
            depth: 200,
            modifier: 1,
            slideShadows: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        speed: 1000
    });

    gsap.from('.showcase-title', {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".product-swiper",
            start: "top 80%",
        }
    });

    // --------------------------------------------------------
    // 8. Stats / Counters Animation
    // --------------------------------------------------------
    const counters = document.querySelectorAll('.counter');
    
    gsap.from('.stats-content > *', {
        x: -50,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".stats-content",
            start: "top 80%",
        }
    });
    
    gsap.from('.stats-grid > div', {
        y: 50,
        opacity: 0,
        duration: 1,
        stagger: 0.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".stats-grid",
            start: "top 80%",
        }
    });

    counters.forEach(counter => {
        ScrollTrigger.create({
            trigger: counter,
            start: "top 85%",
            once: true,
            onEnter: () => {
                const target = +counter.getAttribute('data-target');
                const start = target > 2000 ? 1990 : 0; // Just for visual effect 
                
                const obj = { v: start };
                gsap.to(obj, {
                    v: target,
                    duration: 2.5,
                    ease: "power3.out",
                    onUpdate: () => {
                        counter.innerText = Math.floor(obj.v);
                    }
                });
            }
        });
    });

    // --------------------------------------------------------
    // 9. Contact Section Animations
    // --------------------------------------------------------
    gsap.from('.contact-info > *', {
        x: -50,
        opacity: 0,
        duration: 1,
        stagger: 0.15,
        ease: "power3.out",
        scrollTrigger: {
            trigger: "#contact",
            start: "top 75%",
        }
    });

    gsap.from('.contact-form-wrapper', {
        y: 50,
        opacity: 0,
        scale: 0.95,
        duration: 1.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: "#contact",
            start: "top 75%",
        }
    });
    
    // Smooth scroll for nav anchor links
    document.querySelectorAll('.nav-links a, .mobile-link').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                lenis.scrollTo(href, {
                    offset: -80, // Offset for fixed navbar
                    duration: 1.5
                });
            }
        });
    });

});
