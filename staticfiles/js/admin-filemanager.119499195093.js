/* ==========================================================================
   Admin File Manager JavaScript
   Vanilla JS, no framework/AJAX -- every action here fills in a plain HTML
   form's fields and submits it, so the resulting request is a normal
   multipart POST + full-page redirect, matching the rest of the admin panel.
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {

    // --- Row action buttons (Copy / Cut / quick Delete) share one hidden form ---
    var itemForm = document.getElementById('fmItemActionForm');
    document.querySelectorAll('.fm-row-action').forEach(function (btn) {
        btn.addEventListener('click', function () {
            if (btn.dataset.confirm && !window.confirm(btn.dataset.confirm)) return;
            if (!itemForm) return;
            itemForm.action = btn.dataset.url;
            itemForm.querySelector('[name="item"]').value = btn.dataset.item || '';
            var actionField = itemForm.querySelector('[name="action"]');
            if (actionField) actionField.value = btn.dataset.action || '';
            itemForm.submit();
        });
    });

    // --- Rename modal: populate hidden "item" + visible "name" fields ---
    var renameModalEl = document.getElementById('fmRenameModal');
    if (renameModalEl) {
        renameModalEl.addEventListener('show.bs.modal', function (event) {
            var btn = event.relatedTarget;
            if (!btn) return;
            renameModalEl.querySelector('[name="item"]').value = btn.dataset.item || '';
            var nameInput = renameModalEl.querySelector('[name="name"]');
            nameInput.value = btn.dataset.name || '';
            nameInput.focus();
        });
    }

    // --- Extra confirmation before saving over a live .py file ---
    var editForm = document.getElementById('fmEditForm');
    if (editForm && editForm.dataset.python === 'true') {
        editForm.addEventListener('submit', function (e) {
            if (!window.confirm('You are editing a live application file. A mistake here can break the site. Save anyway?')) {
                e.preventDefault();
            }
        });
    }

    // --- Select-all checkbox for bulk actions ---
    var selectAll = document.getElementById('fmSelectAll');
    if (selectAll) {
        selectAll.addEventListener('change', function () {
            document.querySelectorAll('.fm-row-checkbox').forEach(function (cb) {
                cb.checked = selectAll.checked;
            });
        });
    }

    // --- Bulk delete confirmation ---
    var deleteBtn = document.getElementById('fmDeleteSelected');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function (e) {
            var anyChecked = document.querySelectorAll('.fm-row-checkbox:checked').length > 0;
            if (!anyChecked) {
                e.preventDefault();
                window.alert('Select at least one item first.');
                return;
            }
            if (!window.confirm('Delete the selected items? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    }

    // --- Drag-and-drop upload: populate the file input and auto-submit ---
    var dropZone = document.getElementById('fmDropZone');
    var uploadInput = document.getElementById('fmUploadInput');
    var uploadForm = document.getElementById('fmUploadForm');
    if (dropZone && uploadInput && uploadForm) {
        ['dragenter', 'dragover'].forEach(function (evt) {
            dropZone.addEventListener(evt, function (e) {
                e.preventDefault();
                dropZone.classList.add('fm-dropzone-active');
            });
        });
        ['dragleave', 'drop'].forEach(function (evt) {
            dropZone.addEventListener(evt, function (e) {
                e.preventDefault();
                dropZone.classList.remove('fm-dropzone-active');
            });
        });
        dropZone.addEventListener('drop', function (e) {
            if (e.dataTransfer && e.dataTransfer.files.length) {
                uploadInput.files = e.dataTransfer.files;
                uploadForm.submit();
            }
        });
    }
});
