document.addEventListener('DOMContentLoaded', (event) => {
    const galleryContainers = document.querySelectorAll('.gallery-container');

    galleryContainers.forEach(container => {
        let isDown = false;
        let startX;
        let scrollLeft;

        container.addEventListener('mousedown', (e) => {
            isDown = true;
            container.classList.add('active', 'no-select');
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });

        container.addEventListener('mouseleave', () => {
            isDown = false;
            container.classList.remove('active', 'no-select');
        });

        container.addEventListener('mouseup', () => {
            isDown = false;
            container.classList.remove('active', 'no-select');
        });

        container.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX); // scroll-fast
            container.scrollLeft = scrollLeft - walk;
        });

        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const scrollAmount = e.deltaY;
            const newScrollLeft = container.scrollLeft + scrollAmount;
            container.scrollTo({
                top: 0,
                left: newScrollLeft,
                behavior: 'smooth'
            });
        });
    });
});