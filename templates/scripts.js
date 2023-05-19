document.addEventListener('DOMContentLoaded', () => {
    const classes = ['lang', 'entry-name', 'source', 'gloss', 'word', 'origin', 'clade'];

    const filterEntries = (obj) => {
        const url = new URL('{{ request.url }}', window.location.href);
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
            filter.addEventListener('keydown', event => {
                if (event.keyCode === 13) {
                    className = classes[i].replace('-', '_');
                    obj = {};
                    obj[`${className}`] = event.target.value;
                    filterEntries(obj);
                }
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