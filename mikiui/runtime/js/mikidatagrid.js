(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDataGrid = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      var headers = el.querySelectorAll("th[data-miki-sort-field]");
      for (var i = 0; i < headers.length; i++) {
        (function (th) {
          var field = th.getAttribute("data-miki-sort-field");
          on(th, "click", function () {
            mikiDataGrid.sort(el, field);
          });
          on(th, "keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              mikiDataGrid.sort(el, field);
            }
          });
        })(headers[i]);
      }

      var searchInput = el.querySelector('input[data-miki-search]');
      if (searchInput) {
        var searchTimer = null;
        on(searchInput, "input", function () {
          clearTimeout(searchTimer);
          searchTimer = setTimeout(function () {
            if (el.getAttribute("data-miki-htmx-get")) {
              mikiDataGrid.htmxFetch(el);
            } else {
              mikiDataGrid.applyFilter(el);
            }
          }, 300);
        });
      }

      var filters = el.querySelectorAll('input[data-miki-filter]');
      for (var j = 0; j < filters.length; j++) {
        on(filters[j], "input", function () {
          if (el.getAttribute("data-miki-htmx-get")) {
            mikiDataGrid.htmxFetch(el);
          } else {
            mikiDataGrid.applyFilter(el);
          }
        });
      }

      // Search field select change
      var fieldSelect = el.querySelector('select[name="search_field"]');
      if (fieldSelect) {
        on(fieldSelect, "change", function () {
          if (el.getAttribute("data-miki-htmx-get")) {
            mikiDataGrid.htmxFetch(el);
          } else {
            mikiDataGrid.applyFilter(el);
          }
        });
      }

      mikiDataGrid.updatePaginationState(el);

      var pagination = el.querySelector("[data-miki-pagination]");
      if (pagination) {
        var prevBtn = pagination.querySelector('[data-miki-page="prev"]');
        var nextBtn = pagination.querySelector('[data-miki-page="next"]');
        if (prevBtn) {
          on(prevBtn, "click", function (e) {
            e.preventDefault();
            mikiDataGrid.prevPage(el);
          });
        }
        if (nextBtn) {
          on(nextBtn, "click", function (e) {
            e.preventDefault();
            mikiDataGrid.nextPage(el);
          });
        }
      }
    },

    sort: function (el, field) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;

      var headers = el.querySelectorAll("th[data-miki-sort-field]");
      var colIndex = -1;
      for (var i = 0; i < headers.length; i++) {
        if (headers[i].getAttribute("data-miki-sort-field") === field) {
          colIndex = i;
          break;
        }
      }
      if (colIndex < 0) return;

      var currentField = el.getAttribute("data-miki-sort-field") || "";
      var currentDir = el.getAttribute("data-miki-sort-dir") || "asc";
      var dir = currentField === field ? (currentDir === "asc" ? "desc" : "asc") : "asc";

      el.setAttribute("data-miki-sort-field", field);
      el.setAttribute("data-miki-sort-dir", dir);

      var isNumeric = false;
      for (var h = 0; h < headers.length; h++) {
        if (headers[h].getAttribute("data-miki-sort-field") === field) {
          isNumeric = headers[h].classList.contains("miki-th-number");
          break;
        }
      }

      var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
      var multiplier = dir === "asc" ? 1 : -1;

      rows.sort(function (a, b) {
        var aText = a.cells[colIndex] ? a.cells[colIndex].textContent : "";
        var bText = b.cells[colIndex] ? b.cells[colIndex].textContent : "";
        if (isNumeric) {
          var aNum = parseFloat(aText) || 0;
          var bNum = parseFloat(bText) || 0;
          return aNum < bNum ? -1 * multiplier : aNum > bNum ? 1 * multiplier : 0;
        }
        var aLower = aText.toLowerCase();
        var bLower = bText.toLowerCase();
        return aLower < bLower ? -1 * multiplier : aLower > bLower ? 1 * multiplier : 0;
      });

      rows.forEach(function (r) { tbody.appendChild(r); });

      // Update sort indicators
      for (var k = 0; k < headers.length; k++) {
        var indicator = headers[k].querySelector("[data-miki-sort-indicator]");
        var hField = headers[k].getAttribute("data-miki-sort-field");
        if (indicator) {
          if (hField === field) {
            indicator.textContent = dir === "asc" ? "▲" : "▼";
            indicator.setAttribute("data-dir", dir);
          } else {
            indicator.textContent = "▲";
            indicator.setAttribute("data-dir", "none");
          }
        }
        headers[k].setAttribute("aria-sort",
          hField === field ? (dir === "asc" ? "ascending" : "descending") : "none"
        );
      }

      dispatch(el, "miki:datagrid:sorted", { field: field, dir: dir });
    },

    applyFilter: function (el) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;

      var searchInput = el.querySelector('input[data-miki-search]');
      var searchQuery = searchInput ? searchInput.value.toLowerCase() : "";
      var fieldSelect = el.querySelector('select[name="search_field"]');
      var selectedField = fieldSelect ? fieldSelect.value : "";
      var filterInputs = el.querySelectorAll('input[data-miki-filter]');

      var rows = tbody.querySelectorAll("tr");
      var headers = el.querySelectorAll("th[data-miki-sort-field]");

      // Build field-to-column-index map for targeted search
      var fieldColMap = {};
      for (var h = 0; h < headers.length; h++) {
        var hf = headers[h].getAttribute("data-miki-sort-field");
        if (hf) fieldColMap[hf] = h;
      }

      for (var i = 0; i < rows.length; i++) {
        var rowText = rows[i].textContent.toLowerCase();
        var match = true;

        if (searchQuery) {
          if (selectedField && fieldColMap[selectedField] !== undefined) {
            var colIdx = fieldColMap[selectedField];
            var cellText = rows[i].cells[colIdx] ? rows[i].cells[colIdx].textContent.toLowerCase() : "";
            if (!cellText.includes(searchQuery)) {
              match = false;
            }
          } else {
            if (!rowText.includes(searchQuery)) {
              match = false;
            }
          }
        }

        if (match) {
          for (var j = 0; j < filterInputs.length; j++) {
            var jq = filterInputs[j].value.toLowerCase();
            if (jq) {
              var th = null;
              for (var k = 0; k < headers.length; k++) {
                var fi = headers[k].querySelector('input[data-miki-filter]');
                if (fi === filterInputs[j]) {
                  th = headers[k];
                  break;
                }
              }
              if (th) {
                var colIdx = Array.prototype.indexOf.call(headers, th);
                if (colIdx >= 0 && rows[i].cells[colIdx]) {
                  var cellText = rows[i].cells[colIdx].textContent.toLowerCase();
                  if (!cellText.includes(jq)) {
                    match = false;
                    break;
                  }
                }
              } else {
                if (!rowText.includes(jq)) {
                  match = false;
                  break;
                }
              }
            }
          }
        }

        rows[i].style.display = match ? "" : "none";
      }

      dispatch(el, "miki:datagrid:filtered", { query: searchQuery });
    },

    updatePaginationState: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;

      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;

      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);

      var prevBtn = el.querySelector('[data-miki-page="prev"]');
      var nextBtn = el.querySelector('[data-miki-page="next"]');

      if (prevBtn) prevBtn.disabled = currentPage <= 1;
      if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
    },

    prevPage: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;
      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;
      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);
      if (currentPage > 1) {
        if (el.getAttribute("data-miki-htmx-get")) {
          mikiDataGrid.htmxFetch(el, currentPage - 2);
        } else {
          dispatch(el, "miki:datagrid:navigate", { page: currentPage - 2, totalPages: totalPages });
        }
      }
    },

    nextPage: function (el) {
      var info = el.querySelector("[data-miki-page-info]");
      if (!info) return;
      var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
      if (!match) return;
      var currentPage = parseInt(match[1], 10);
      var totalPages = parseInt(match[2], 10);
      if (currentPage < totalPages) {
        if (el.getAttribute("data-miki-htmx-get")) {
          mikiDataGrid.htmxFetch(el, currentPage);
        } else {
          dispatch(el, "miki:datagrid:navigate", { page: currentPage, totalPages: totalPages });
        }
      }
    },

    htmxFetch: function (el, pageNum) {
      var url = el.getAttribute("data-miki-htmx-get");
      if (!url) return;

      var params = new URLSearchParams();
      var sortField = el.getAttribute("data-miki-sort-field") || "";
      if (sortField) params.set("sort_field", sortField);
      var sortDir = el.getAttribute("data-miki-sort-dir") || "";
      if (sortDir) params.set("sort_dir", sortDir);
      var searchInput = el.querySelector('input[data-miki-search]');
      if (searchInput && searchInput.value) params.set("search", searchInput.value);
      var fieldSelect = el.querySelector('select[name="search_field"]');
      if (fieldSelect && fieldSelect.value) params.set("search_field", fieldSelect.value);
      if (pageNum !== undefined) params.set("page", pageNum);

      var target = el.getAttribute("data-miki-htmx-target") || el.id;
      if (!target) return;

      var fullUrl = url + (url.indexOf("?") === -1 ? "?" : "&") + params.toString();

      var xhr = new XMLHttpRequest();
      xhr.open("GET", fullUrl, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            var targetEl = document.querySelector(target);
             if (targetEl) {
               targetEl.innerHTML = xhr.responseText;
               if (window.MikiUI && MikiUI.init) {
                 MikiUI.init(targetEl);
               }
             }
          }
          dispatch(el, "miki:datagrid:fetched", { page: pageNum, success: xhr.status === 200 });
        }
      };
      xhr.send();
    }
  };

  window.mikiDataGrid = mikiDataGrid;
})();
