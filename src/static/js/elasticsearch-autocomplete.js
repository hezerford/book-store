// Elasticsearch Autocomplete
class ElasticsearchAutocomplete {
    constructor(inputElement, resultsContainer, options = {}) {
        this.input = inputElement;
        this.resultsContainer = resultsContainer;
        this.options = {
            minLength: 2,
            delay: 300,
            maxResults: 10,
            ...options
        };

        this.timeout = null;
        this.isSearching = false;

        this.init();
    }

    init() {
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('blur', this.handleBlur.bind(this));
        this.input.addEventListener('focus', this.handleFocus.bind(this));

        // Скрываем результаты при клике вне поля
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }

    handleInput(e) {
        const query = e.target.value.trim();

        // Очищаем предыдущий таймаут
        if (this.timeout) {
            clearTimeout(this.timeout);
        }

        // Если запрос слишком короткий, скрываем результаты
        if (query.length < this.options.minLength) {
            this.hideResults();
            return;
        }

        // Устанавливаем задержку перед поиском
        this.timeout = setTimeout(() => {
            this.search(query);
        }, this.options.delay);
    }

    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= this.options.minLength) {
            this.search(query);
        }
    }

    handleBlur(e) {
        // Небольшая задержка, чтобы пользователь мог кликнуть на результат
        setTimeout(() => {
            this.hideResults();
        }, 200);
    }

    async search(query) {
        if (this.isSearching) return;

        this.isSearching = true;
        this.showLoading();

        try {
            const response = await fetch(`/search/?format=json&query=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.displayResults(data.results);
        } catch (error) {
            console.error('Search error:', error);
            this.hideResults();
        } finally {
            this.isSearching = false;
        }
    }

    showLoading() {
        this.resultsContainer.innerHTML = '<div class="autocomplete-loading">Searching...</div>';
        this.resultsContainer.style.display = 'block';
    }

    displayResults(results) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = '<div class="autocomplete-no-results">No results found</div>';
        } else {
            let html = '';
            results.forEach(result => {
                html += `
                    <div class="autocomplete-item" data-url="${result.url}">
                        <div class="autocomplete-title">${this.highlightMatch(result.title, this.input.value)}</div>
                        <div class="autocomplete-author">by ${this.highlightMatch(result.author, this.input.value)}</div>
                    </div>
                `;
            });
            this.resultsContainer.innerHTML = html;

            // Добавляем обработчики кликов
            this.resultsContainer.querySelectorAll('.autocomplete-item').forEach(item => {
                item.addEventListener('click', () => {
                    window.location.href = item.dataset.url;
                });
            });
        }

        this.resultsContainer.style.display = 'block';
    }

    highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    hideResults() {
        this.resultsContainer.style.display = 'none';
    }
}

// Инициализация автодополнения
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('input[name="query"]');
    const resultsContainer = document.getElementById('search-results');

    if (searchInput && resultsContainer) {
        new ElasticsearchAutocomplete(searchInput, resultsContainer);
    }
});
