/**
 * Live Markdown Preview
 * Sends current editor content to the server for rendering.
 */
(function () {
    'use strict';

    var previewPane = null;
    var previewContent = null;
    var editor = null;
    var timer = null;

    function init() {
        previewPane = document.getElementById('preview-pane');
        previewContent = document.getElementById('preview-content');
        editor = document.querySelector('.markdown-editor');

        if (!previewPane || !editor) return;

        // Toggle preview visibility
        var toggleBtn = document.querySelector('.editor-toolbar .btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function () {
                if (previewPane.style.display === 'none') {
                    previewPane.style.display = 'block';
                    fetchPreview();
                } else {
                    previewPane.style.display = 'none';
                }
            });
        }

        // Auto-refresh preview while typing
        editor.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(fetchPreview, 500);
        });
    }

    function fetchPreview() {
        if (!editor || !previewContent) return;

        var formData = new FormData();
        formData.append('body', editor.value);
        var titleInput = document.querySelector('input[name="title"]');
        if (titleInput) {
            formData.append('title', titleInput.value);
        }

        fetch('/admin/posts/preview-inline', {
            method: 'POST',
            body: formData
        })
            .then(function (response) {
                return response.text();
            })
            .then(function (html) {
                previewContent.innerHTML = html;
            })
            .catch(function () {
                previewContent.innerHTML = '<p style="color:red">预览加载失败</p>';
            });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
