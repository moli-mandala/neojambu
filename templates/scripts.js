document.addEventListener('DOMContentLoaded', () => {

    const classes = ['lang', 'origin-lang', 'entry-name', 'source', 'gloss', 'word', 'origin', 'clade', 'notes', 'reflexes'];
    const special_chars = ['ṭ', 'ḍ', 'ṣ', 'ṛ', 'r̩', 'ṁ', 'ʰ'];
    var pal = document.createElement("div");
    pal.classList.add("palette");
    pal.classList.add("hidden");
    special_chars.forEach(char => {
        var span = document.createElement("span");
        span.textContent = char;
        pal.appendChild(span);
    });
    var origUrl = `{{ request.url }}`
    var results = document.querySelector('.results');

    // create node
    var loader = document.createElement("tr");
    var temp = $('<div/>');
    loader.classList.add("loader-line");
    loader.classList.add("hidden");
    results.prepend(loader);

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
        const classList = document.querySelectorAll(`input.${classes[i]}-filter`);
        classList.forEach(filter => {
            let orig_value = filter.value;

            // add palette
            let palette = pal.cloneNode(true);
            let className = classes[i].replace('-', '_');
            palette.style.left = filter.offsetLeft + 'px';
            palette.style.top = filter.offsetTop + filter.offsetHeight + 'px';
            palette.addEventListener('click', event => {
                if (event.target.tagName === 'SPAN') {
                    filter.value += event.target.textContent;
                    filter.focus();
                    obj = {};
                    obj[`${className}`] = filter.value;
                    filterEntries(obj);
                }
            });
            filter.parentNode.appendChild(palette);

            filter.addEventListener('keyup', event => {
                loader.classList.remove('hidden');
                let new_value = event.target.value;
                setTimeout(function() {
                    if (filter.value === new_value) {
                        obj = {};
                        obj[`${className}`] = filter.value;
                        filterEntries(obj);
                    }
                }, 300);
            });
            filter.addEventListener('focus', event => {
                palette.classList.remove('hidden');
            });
            filter.addEventListener('blur', event => {
                setTimeout(function() {
                    if (document.activeElement !== filter) {palette.classList.add('hidden');}
                }, 300);
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