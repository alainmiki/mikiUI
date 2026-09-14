(function () {
  "use strict";

  var miki = window.miki || {};

  var mikiDataGrid = {
    init: function (el) {
      if (el.dataset.mikiInit === "true") return;
      el.dataset.mikiInit = "true";

      mikiDataGrid._rows = [];
      mikiDataGrid._parseRows(el);
      mikiDataGrid.processData(el);

      var headerHandlers = [];
      var headers = el.querySelectorAll("th[data-miki-sort-field]");
      for (var i = 0; i < headers.length; i++) {
        (function (th) {
          var field = th.getAttribute("data-miki-sort-field");
          var clickHandler = function () { mikiDataGrid.sort(el, field); };
          var keyHandler = function (e) {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              mikiDataGrid.sort(el, field);
            }
          };
          on(th, "click", clickHandler);
          on(th, "keydown", keyHandler);
          headerHandlers.push({ el: th, event: "click", handler: clickHandler, opts: false });
          headerHandlers.push({ el: th, event: "keydown", handler: keyHandler, opts: false });
        })(headers[i]);
      }

      var searchInput = el.querySelector('input[data-miki-search]');
      var searchTimer = null;
      var searchHandler = null;
      if (searchInput) {
        searchHandler = function () {
          clearTimeout(searchTimer);
          searchTimer = setTimeout(function () {
            if (el.getAttribute("data-miki-htmx-get")) {
              mikiDataGrid.htmxFetch(el);
            } else {
              mikiDataGrid.applyFilter(el);
            }
          }, 300);
        };
        on(searchInput, "input", searchHandler);
        headerHandlers.push({ el: searchInput, event: "input", handler: searchHandler, opts: false });
      }

      var filterHandlers = [];
      var filters = el.querySelectorAll('input[data-miki-filter]');
      for (var j = 0; j < filters.length; j++) {
        (function (filterInput) {
          var filterHandler = function () {
            if (el.getAttribute("data-miki-htmx-get")) {
              mikiDataGrid.htmxFetch(el);
            } else {
              mikiDataGrid.applyFilter(el);
            }
          };
          on(filterInput, "input", filterHandler);
          filterHandlers.push({ el: filterInput, event: "input", handler: filterHandler, opts: false });
        })(filters[j]);
      }

      var fieldSelect = el.querySelector('select[name="search_field"]');
      var fieldHandler = null;
      if (fieldSelect) {
        fieldHandler = function () {
          if (el.getAttribute("data-miki-htmx-get")) {
            mikiDataGrid.htmxFetch(el);
          } else {
            mikiDataGrid.applyFilter(el);
          }
        };
        on(fieldSelect, "change", fieldHandler);
        headerHandlers.push({ el: fieldSelect, event: "change", handler: fieldHandler, opts: false });
      }

      mikiDataGrid.updatePaginationState(el);

      var pagination = el.querySelector("[data-miki-pagination]");
      var paginationHandlers = [];
      if (pagination) {
        var prevBtn = pagination.querySelector('[data-miki-page="prev"]');
        var nextBtn = pagination.querySelector('[data-miki-page="next"]');
        if (prevBtn) {
          var prevHandler = function (e) {
            e.preventDefault();
            mikiDataGrid.prevPage(el);
          };
          on(prevBtn, "click", prevHandler);
          paginationHandlers.push({ el: prevBtn, event: "click", handler: prevHandler, opts: false });
        }
        if (nextBtn) {
          var nextHandler = function (e) {
            e.preventDefault();
            mikiDataGrid.nextPage(el);
          };
          on(nextBtn, "click", nextHandler);
          paginationHandlers.push({ el: nextBtn, event: "click", handler: nextHandler, opts: false });
        }
      }

      registerDestroyHandler(el, function () {
        for (var k = 0; k < headerHandlers.length; k++) {
          var h = headerHandlers[k];
          off(h.el, h.event, h.handler, h.opts);
        }
        for (var l = 0; l < filterHandlers.length; l++) {
          var fh = filterHandlers[l];
          off(fh.el, fh.event, fh.handler, fh.opts);
        }
        for (var m = 0; m < paginationHandlers.length; m++) {
          var ph = paginationHandlers[m];
          off(ph.el, ph.event, ph.handler, ph.opts);
        }
        if (searchTimer) clearTimeout(searchTimer);
      });
    },

    destroy: function (el) {
      mikiDestroy(el);
    },

    _parseRows: function (el) {
      var raw = el.getAttribute("data-miki-rows");
      if (!raw) {
        mikiDataGrid._rows = [];
        return;
      }
      try {
        mikiDataGrid._rows = JSON.parse(raw);
      } catch (e) {
        mikiDataGrid._rows = [];
      }
    },

    _escapeRegex: function (str) {
      return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    },

    _getPageInfo: function (el) {
      var page = 0;
      var pageSize = 10;
      var infoEl = el.querySelector("[data-miki-page-info]");
      if (infoEl) {
        var match = infoEl.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
        if (match) {
          page = parseInt(match[1], 10) - 1;
        }
      }
      var sizeAttr = el.getAttribute("data-miki-page-size");
      if (sizeAttr) pageSize = parseInt(sizeAttr, 10);
      return { page: page, pageSize: pageSize };
    },

    _getFilteredRows: function (el) {
      var searchInput = el.querySelector('input[data-miki-search]');
      var searchQuery = searchInput ? searchInput.value.trim() : "";
      var fieldSelect = el.querySelector('select[name="search_field"]');
      var selectedField = fieldSelect ? fieldSelect.value : "";
      var filterInputs = el.querySelectorAll('input[data-miki-filter]');
      var headers = el.querySelectorAll("th[data-miki-sort-field]");

      var fieldColMap = {};
      for (var h = 0; h < headers.length; h++) {
        var hf = headers[h].getAttribute("data-miki-sort-field");
        if (hf) fieldColMap[hf] = h;
      }

      var rows = mikiDataGrid._rows.slice();
      var result = [];

      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (!row || typeof row !== "object") { result.push(row); continue; }
        var match = true;
        var rowKeys = Object.keys(row);

        if (searchQuery) {
          match = false;
          if (selectedField && fieldColMap[selectedField] !== undefined) {
            var cellVal = String(row[selectedField] || "");
            if (cellVal.toLowerCase().indexOf(searchQuery.toLowerCase()) >= 0) match = true;
          } else {
            for (var k = 0; k < rowKeys.length; k++) {
              if (String(row[rowKeys[k]] || "").toLowerCase().indexOf(searchQuery.toLowerCase()) >= 0) {
                match = true;
                break;
              }
            }
          }
        }

        if (match) {
          for (var j = 0; j < filterInputs.length; j++) {
            var jq = filterInputs[j].value.trim().toLowerCase();
            if (!jq) continue;
            var th = null;
            for (var k2 = 0; k2 < headers.length; k2++) {
              var fi = headers[k2].querySelector('input[data-miki-filter]');
              if (fi === filterInputs[j]) { th = headers[k2]; break; }
            }
            var matched = false;
            if (th) {
              var thField = th.getAttribute("data-miki-sort-field");
              var cellText = String(row[thField] || "").toLowerCase();
              if (cellText.indexOf(jq) >= 0) matched = true;
            } else {
              for (var k3 = 0; k3 < rowKeys.length; k3++) {
                if (String(row[rowKeys[k3]] || "").toLowerCase().indexOf(jq) >= 0) {
                  matched = true; break;
                }
              }
            }
            if (!matched) { match = false; break; }
          }
        }

        if (match) result.push(row);
      }

      return result;
    },

    processData: function (el) {
      var tbody = el.querySelector("tbody");
      if (!tbody) return;

      var filtered = mikiDataGrid._getFilteredRows(el);
      var pageInfo = mikiDataGrid._getPageInfo(el);
      var page = pageInfo.page;
      var pageSize = pageInfo.pageSize;
      var totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
      if (page >= totalPages) page = totalPages - 1;
      if (page < 0) page = 0;
      var start = page * pageSize;
      var end = start + pageSize;
      var pageRows = filtered.slice(start, end);

      tbody.innerHTML = "";
      if (pageRows.length === 0) {
        var emptyTr = document.createElement("tr");
        var emptyTd = document.createElement("td");
        emptyTd.setAttribute("colspan", "99");
        emptyTd.style.textAlign = "center";
        emptyTd.style.color = "var(--miki-text-muted, #64748b)";
        emptyTd.style.padding = "1rem";
        emptyTd.textContent = "No matching records found.";
        emptyTr.appendChild(emptyTd);
        tbody.appendChild(emptyTr);
      } else {
        for (var i = 0; i < pageRows.length; i++) {
          var row = pageRows[i];
          var tr = document.createElement("tr");
          tr.setAttribute("role", "row");
          tr.classList.add("miki-tr");
          var keys = Object.keys(row);
          for (var j = 0; j < keys.length; j++) {
            var td = document.createElement("td");
            td.textContent = String(row[keys[j]] || "");
            tr.appendChild(td);
          }
          tbody.appendChild(tr);
        }
      }

      var pageInfoEl = el.querySelector("[data-miki-page-info]");
      if (pageInfoEl) {
        pageInfoEl.textContent = "Page " + (page + 1) + " of " + totalPages;
      }

      var prevBtn = el.querySelector('[data-miki-page="prev"]');
      var nextBtn = el.querySelector('[data-miki-page="next"]');
      if (prevBtn) prevBtn.disabled = page <= 0;
      if (nextBtn) nextBtn.disabled = page >= totalPages - 1;

      el.setAttribute("data-miki-current-page", String(page));

      dispatch(el, "miki:datagrid:processed", { page: page, totalPages: totalPages, rowCount: filtered.length });
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
      if (el.getAttribute("data-miki-htmx-get")) {
        mikiDataGrid.htmxFetch(el);
      } else {
        mikiDataGrid.processData(el);
      }
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
      if (el.getAttribute("data-miki-htmx-get")) {
        var info = el.querySelector("[data-miki-page-info]");
        if (!info) return;
        var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
        if (!match) return;
        var currentPage = parseInt(match[1], 10);
        var totalPages = parseInt(match[2], 10);
        if (currentPage > 1) {
          mikiDataGrid.htmxFetch(el, currentPage - 1);
        }
      } else {
        var pageInfo = mikiDataGrid._getPageInfo(el);
        var newPage = pageInfo.page - 1;
        if (newPage >= 0) {
          var infoEl2 = el.querySelector("[data-miki-page-info]");
          if (infoEl2) {
            var m2 = infoEl2.textContent.match(/Page\s*\d+\s*of\s*(\d+)/);
            if (m2) {
              var tp = parseInt(m2[1], 10);
              if (newPage >= tp) newPage = tp - 1;
            }
          }
          el.setAttribute("data-miki-current-page", String(newPage));
          mikiDataGrid.processData(el);
        }
      }
    },

    nextPage: function (el) {
      if (el.getAttribute("data-miki-htmx-get")) {
        var info = el.querySelector("[data-miki-page-info]");
        if (!info) return;
        var match = info.textContent.match(/Page\s*(\d+)\s*of\s*(\d+)/);
        if (!match) return;
        var currentPage = parseInt(match[1], 10);
        var totalPages = parseInt(match[2], 10);
        if (currentPage < totalPages) {
          mikiDataGrid.htmxFetch(el, currentPage + 1);
        }
      } else {
        var pageInfo2 = mikiDataGrid._getPageInfo(el);
        var infoEl3 = el.querySelector("[data-miki-page-info]");
        var totalPages2 = 1;
        if (infoEl3) {
          var m3 = infoEl3.textContent.match(/Page\s*\d+\s*of\s*(\d+)/);
          if (m3) totalPages2 = parseInt(m3[1], 10);
        }
        var newPage2 = pageInfo2.page + 1;
        if (newPage2 < totalPages2) {
          el.setAttribute("data-miki-current-page", String(newPage2));
          mikiDataGrid.processData(el);
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
