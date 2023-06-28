document.addEventListener('DOMContentLoaded', () => {
    const classes = ['lang', 'origin-lang', 'entry-name', 'source', 'gloss', 'word', 'origin', 'clade', 'notes', 'reflexes'];
    var origUrl = `{{ request.url }}`
    var results = document.querySelector('.results');
    // create node
    var loader = document.createElement("tr");
    var temp = $('<div/>');
    loader.classList.add("loader-line");
    const filterEntries = (obj) => {
        // add loading spinner to start of results
        results.prepend(loader);
        const url = new URL(origUrl, window.location.href);
        for (key in obj) {
            url.searchParams.set(key, obj[key]);
        }
        if (!('page' in obj)) {
            url.searchParams.delete('page');
        }
        console.log(url)
        window.history.pushState({}, null, url);

        temp.load(url + ' .results, .showing, .page', function () {
            $('.results').html($('.results > *', temp));
            $('.page').html($('.page > *', temp));
            $('.showing').html($('.showing', temp));
            // page navigation
            const pageNav = document.querySelectorAll('.page-nav');
            pageNav.forEach(nav => {
                nav.addEventListener('click', event => {
                    filterEntries({ page: event.target.dataset.page });
                });
            });
            origUrl = url;
        });
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

        const filter2 = document.querySelectorAll(`select.${classes[i]}-filter`);
        filter2.forEach(filter => {
            filter.addEventListener('change', event => {
                className = classes[i].replace('-', '_');
                obj = {};
                obj[`${className}`] = event.target.value;
                filterEntries(obj);
            });
        });


        const asc = document.querySelectorAll(`.${classes[i]}-asc`);
        asc.forEach(filter => {
            filter.addEventListener('click', event => {
                className = classes[i].replace('-', '_');
                obj = {};
                obj['sort'] = event.target.classList.contains('arrow-active') ? '' : `asc-${className}`;
                filterEntries(obj);
                $('.arrow-active').removeClass('arrow-active');
                if (obj['sort'] !== '') {
                    event.target.classList.add('arrow-active');
                }
            });
        });


        const desc = document.querySelectorAll(`.${classes[i]}-desc`);
        desc.forEach(filter => {
            filter.addEventListener('click', event => {
                className = classes[i].replace('-', '_');
                obj = {};
                obj['sort'] = event.target.classList.contains('arrow-active') ? '' : `desc-${className}`;
                filterEntries(obj);
                $('.arrow-active').removeClass('arrow-active');
                if (obj['sort'] !== '') {
                    event.target.classList.add('arrow-active');
                }
            });
        });
    }

    // page navigation
    const pageNav = document.querySelectorAll('.page-nav');
    pageNav.forEach(nav => {
        nav.addEventListener('click', event => {
            filterEntries({ page: event.target.dataset.page });
        });
    });
});