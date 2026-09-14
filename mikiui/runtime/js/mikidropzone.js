(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDropzone = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var fileInput = el.querySelector('[data-miki-file-input="true"]');
      if (!fileInput) return;

      var clickHandler = function () {
        fileInput.click();
      };
      on(el, "click", clickHandler);

      var keyHandler = function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          fileInput.click();
        }
      };
      on(el, "keydown", keyHandler);

      var prevent = function (e) {
        e.preventDefault();
        e.stopPropagation();
      };

      var dragEnterHandler = function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      };
      on(el, "dragenter", dragEnterHandler);

      var dragOverHandler = function (e) {
        prevent(e);
        el.classList.add("miki-drag-over");
      };
      on(el, "dragover", dragOverHandler);

      var dragLeaveHandler = function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
      };
      on(el, "dragleave", dragLeaveHandler);

      var dropHandler = function (e) {
        prevent(e);
        el.classList.remove("miki-drag-over");
        var files = e.dataTransfer.files;
        if (files && files.length > 0) {
          fileInput.files = files;
          el.setAttribute("data-files", files.length);
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
      };
      on(el, "drop", dropHandler);

      var changeHandler = function () {
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
      };
      on(fileInput, "change", changeHandler);

      registerDestroyHandler(el, function () {
        off(el, "click", clickHandler);
        off(el, "keydown", keyHandler);
        off(el, "dragenter", dragEnterHandler);
        off(el, "dragover", dragOverHandler);
        off(el, "dragleave", dragLeaveHandler);
        off(el, "drop", dropHandler);
        off(fileInput, "change", changeHandler);
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    }
  };

  window.mikiDropzone = mikiDropzone;
})();
