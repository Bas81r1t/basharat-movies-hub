// index.js

// ---- Module safe check ----
(function(){
  // ---- Ultra smooth 120Hz easing ----
  function iosEasing(t){ return t<0.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2; }

  // ---- Lenis Smooth Scroll ----
  if (typeof Lenis !== 'undefined') {
    const lenis = new Lenis({
      wrapper: document.querySelector('#lenis-wrapper'),
      content: document.querySelector('#lenis-content'),
      duration: 1.2,
      easing: iosEasing,
      direction: 'vertical',
      smooth: true,
      lerp: 0.12,
      wheelMultiplier: 1.2,
      smoothTouch: true
    });

    function raf(time){
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Anchor smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor=>{
      anchor.addEventListener('click', e=>{
        e.preventDefault();
        const target=document.querySelector(anchor.getAttribute('href'));
        if(target) lenis.scrollTo(target,{duration:1.2,easing:iosEasing});
      });
    });
  } else {
    console.warn("⚠ Lenis not loaded!");
  }

  // ---- Navbar shadow on scroll ----
  window.addEventListener('scroll',()=>{
    const navbar=document.querySelector('.navbar');
    if(window.scrollY>50) navbar.classList.add('navbar-scrolled');
    else navbar.classList.remove('navbar-scrolled');
  });

  // ---- Section fade-in on scroll ----
  const sections = document.querySelectorAll('.scroll-section');
  function checkSections(){
    const scrollTop = window.scrollY || window.pageYOffset;
    sections.forEach(section=>{
      if(section.offsetTop < scrollTop + window.innerHeight - 100){
        section.classList.add('active');
      }
    });
  }
  window.addEventListener('scroll', checkSections);
  checkSections();

  // ---- Install Tracker Integration ----


})();
