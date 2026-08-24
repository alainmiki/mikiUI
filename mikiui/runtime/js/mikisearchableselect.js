(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiSearchableSelect = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      // Wrap native select in a container with a filter input
      var filterInput = document.createElement("input");
      filterInput.type = "text";
      filterInput.className = "miki-searchable-filter";
      filterInput.placeholder = "Type to filter...";
      filterInput.setAttribute("autocomplete", "off");

      var wrapper = document.createElement("div");
      wrapper.className = "miki-searchable-wrapper";
      wrapper.style.position = "relative";
      wrapper.style.display = "inline-block";
      wrapper.style.width = el.style.width || "100%";

      el.parentNode.insertBefore(wrapper, el);
      wrapper.appendChild(filterInput);
      wrapper.appendChild(el);

      on(filterInput, "input", function () {
        var filter = filterInput.value.toLowerCase();
        var options = el.querySelectorAll("option");
        var matchFound = false;
        for (var i = 0; i < options.length; i++) {
          var text = options[i].textContent.toLowerCase();
          if (text.indexOf(filter) > -1) {
            options[i].style.display = "";
            matchFound = true;
          } else {
            options[i].style.display = "none";
          }
        }
      });
    }
  };

  window.mikiSearchableSelect = mikiSearchableSelect;
})();
