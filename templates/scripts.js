document.addEventListener('DOMContentLoaded', () => {
    const classes = ['lang', 'entry-name', 'source', 'gloss', 'word', 'origin', 'clade', 'notes'];

    const filterEntries = (obj) => {
        const url = new URL(`{{ request.url }}`, window.location.href);
        for (key in obj) {
            url.searchParams.set(key, obj[key]);
        }
        if (!('page' in obj)) {
            url.searchParams.delete('page');
        }
        console.log(url)
        window.location.href = url;
    }

    for (let i = 0; i < classes.length; i++) {
        const classList = document.querySelectorAll(`.${classes[i]}-filter`);
        classList.forEach(filter => {
            let orig_value = filter.value;
            filter.addEventListener('keydown', event => {
                if (event.keyCode === 13) {
                    className = classes[i].replace('-', '_');
                    obj = {};
                    obj[`${className}`] = event.target.value;
                    filterEntries(obj);
                }
            });
            filter.addEventListener('focus', event => {
                orig_value = event.target.value;
            });
            filter.addEventListener('blur', event => {
                if (event.target.value !== orig_value) {
                    className = classes[i].replace('-', '_');
                    obj = {};
                    obj[`${className}`] = event.target.value;
                    filterEntries(obj);
                }
                orig_value = event.target.value;
            });
        });
    }

    const languageFilters2 = document.querySelectorAll('select.lang-filter');
    languageFilters2.forEach(filter => {
        filter.addEventListener('change', event => {
            filterEntries({ lang: event.target.value });
        });
    });

    // page navigation
    const pageNav = document.querySelectorAll('.page-nav');
    pageNav.forEach(nav => {
        nav.addEventListener('click', event => {
            filterEntries({ page: event.target.dataset.page });
        });
    });
});