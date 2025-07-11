// app/static/js/editor.js

document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelector('textarea[name="content"]')) {
        tinymce.init({
            selector: 'textarea[name="content"]',
            height: 300,
            plugins: 'advlist autolink link image lists charmap preview anchor pagebreak',
            toolbar: 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | outdent indent',
            menubar: false
        });
    }
});
