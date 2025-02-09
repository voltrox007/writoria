// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.backgroundColor = '#fff';
        navbar.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    } else {
        navbar.style.backgroundColor = 'transparent';
        navbar.style.boxShadow = 'none';
    }
});

// Add smooth scrolling
document.querySelector('.start-reading').addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelector('.posts-container').scrollIntoView({
        behavior: 'smooth'
    });
});

// Add reading time calculation
document.querySelectorAll('.post-card').forEach(post => {
    const content = post.querySelector('p').textContent;
    const wordCount = content.split(' ').length;
    const readingTime = Math.ceil(wordCount / 200); // Average reading speed of 200 words per minute
    
    const meta = post.querySelector('.post-meta');
    const timeSpan = document.createElement('span');
    timeSpan.textContent = ` · ${readingTime} min read`;
    meta.appendChild(timeSpan);
});