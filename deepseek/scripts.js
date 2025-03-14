// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    const items = document.querySelectorAll('.item');

    items.forEach(item => {
        item.addEventListener('click', () => {
            alert('你點擊了 ' + item.querySelector('h3').textContent);
        });
    });
});