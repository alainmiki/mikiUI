(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDropzone = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var fileInput = el.querySelector('[data-miki-file-input="true"]');
      if (!fileInput) return;

      on(el, "click", function () {
        fileInput.click();
      });

      on(el, "keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          fileInput.click();
        }
      });

      var prevent = function (e) {
        e.preventDefault();
        e.stopPropagation();
      };

      on(el, "dragenter", function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      });

      on(el, "dragover", function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      });

      on(el, "dragleave", function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
      });

      on(el, "drop", function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
        var files = e.dataTransfer.files;
        if (files && files.length > 0) {
          fileInput.files = files;
          el.setAttribute("data-files", files.length);
          // Update the visible label with the dropped file names
          var label = el.querySelector(".miki-dropzone-label");
          if (label) {
            var names = [];
            for (var i = 0; i < files.length; i++) {
              names.push(files[i].name);
            }
            label.textContent = names.length === 1
              ? names[0]
              : names.join(", ") + " (" + files.length + " files)";
            label.classList.add("miki-has-files");
          }
          dispatch(el, "miki:files:dropped", { files: files });
        }
      });

      on(fileInput, "change", function () {
        if (fileInput.files && fileInput.files.length > 0) {
          var label = el.querySelector(".miki-dropzone-label");
          if (label) {
            var names = [];
            for (var i = 0; i < fileInput.files.length; i++) {
              names.push(fileInput.files[i].name);
            }
            label.textContent = names.length === 1
              ? names[0]
              : names.join(", ") + " (" + fileInput.files.length + " files)";
            label.classList.add("miki-has-files");
          }
          el.setAttribute("data-files", fileInput.files.length);
          dispatch(el, "miki:files:selected", { files: fileInput.files });
        }
      });
    }
  };

  window.mikiDropzone = mikiDropzone;
})();
