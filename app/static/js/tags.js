/**
 * Tags interaction helpers
 */
(function () {
    'use strict';

    /**
     * Convert comma-separated tag string to a list of existing tag suggestions.
     * This is a lightweight helper — full autocomplete would require a backend API.
     */
    function initTagSuggestions() {
        var tagInput = document.querySelector('input[name="tags"]');
        if (!tagInput) return;

        // Get existing tags from the page (injected as a data attribute or hidden element)
        var tagDataEl = document.getElementById('existing-tags');
        if (!tagDataEl) return;

        var existingTags = JSON.parse(tagDataEl.dataset.tags || '[]');

        tagInput.setAttribute('list', 'tag-suggestions');

        var dl = document.getElementById('tag-datalist');
        if (!dl) {
            dl = document.createElement('datalist');
            dl.id = 'tag-datalist';
            document.body.appendChild(dl);
        }

        existingTags.forEach(function (tag) {
            var option = document.createElement('option');
            option.value = tag;
            dl.appendChild(option);
        });
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTagSuggestions);
    } else {
        initTagSuggestions();
    }
})();
