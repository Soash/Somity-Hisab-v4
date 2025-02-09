document.addEventListener("DOMContentLoaded", function() {
    const bodyClass = document.body.classList;
    if (bodyClass.contains('theme-dark')) {
        bodyClass.remove('theme-dark');
        bodyClass.add('theme-light');
    }
});
