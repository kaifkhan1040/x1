/**
 * DataTables Basic
 */

'use strict';

let fv, offCanvasEl;
document.addEventListener('DOMContentLoaded', function (e) {
  (function () {
   

    // FlatPickr Initialization & Validation
    const flatpickrDate = document.querySelector('[name="basicDate"]');

    if (flatpickrDate) {
      flatpickrDate.flatpickr({
        enableTime: false,
        monthSelectorType: 'static',
        static: true,
        // See https://flatpickr.js.org/formatting/
        dateFormat: 'm/d/Y',
        // After selecting a date, we need to revalidate the field
        onChange: function () {
          fv.revalidateField('basicDate');
        }
      });
    }
  })();

  // init function
  const dt_basic_table = document.querySelector('.datatables-basic');
  let dt_basic;

  if (dt_basic_table) {
    const tenantFilters = document.querySelector('.tenant-filters');
    const currencySymbol = dt_basic_table.dataset.currencySymbol || '';
    const renderCurrency = function (value, type) {
      if (type !== 'display' || value === null || value === undefined || value === '') return value;
      const amount = Number(value);
      return Number.isFinite(amount) ? `${currencySymbol}${amount.toFixed(2)}` : value;
    };
    let tableTitle = document.createElement('h5');
    tableTitle.classList.add('card-title', 'mb-0', 'text-md-start', 'text-center', 'pb-0');
    // tableTitle.innerHTML = 'Tenants';
    dt_basic = new DataTable(dt_basic_table, {
      ajax: {
                    url: '/landlord/tenant_list',
                    dataSrc: 'data'
                },
      columns: [
        {
        data: null,
        render: function (data, type, full, meta) {
            return ''; // Or some icon / row index
        }
    },
    {
        data: null,
        render: function (data, type, full, meta) {
            return (
                '<div class="form-check">' +
                '<input class="form-check-input dt-checkboxes" type="checkbox" value="" id="checkbox' +
                meta.row +
                '" />' +
                '<label class="form-check-label" for="checkbox' +
                meta.row +
                '"></label></div>'
            );
        },
        checkboxes: {
            selectAllRender:
                '<div class="form-check"> <input class="form-check-input" type="checkbox" value="" id="checkboxSelectAll" /><label class="form-check-label" for="checkboxSelectAll"></label></div>'
        }
    },
    {
        data: 'sr',
        render: function (data, type, full, meta) {
          return meta.settings._iDisplayStart + meta.row + 1;
        }
    },
    {
        data: 'full_name',
        render: function (data, type, full) {
          if (type !== 'display') return data;
          const name = String(data || '—').replace(/[&<>"']/g, char => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
          })[char]);
          return `<a href="/landlord/tenant-dashboard/${full.id}/">${name}</a>`;
        }
    },
    { data: 'room', defaultContent: '' },
    { data: 'property', defaultContent: '' },
    { data: 'rent', render: renderCurrency },
    { data: 'total_dues', render: renderCurrency },
    {
        data: null,
        orderable: false,
        searchable: false,
        render: function (data, type, full) {
          if (type !== 'display') return '';
          return `<div class="dropdown">
            <button class="btn btn-sm btn-icon dropdown-toggle hide-arrow" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Tenant actions">
              <i class="icon-base ti tabler-dots-vertical"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><a class="dropdown-item" href="/landlord/tenant-dashboard/${full.id}/">View profile</a></li>
              <li><a class="dropdown-item" href="/landlord/tenant-update/${full.id}/">Edit tenant</a></li>
            </ul>
          </div>`;
        }
    }
      ],
      columnDefs: [
        {
          // For Responsive
           className: 'control',
          orderable: false,
          responsivePriority: 2,
          targets: 0
        },
        {
          // For Checkboxes
          targets: 1,
          orderable: false,
          searchable: false,
          responsivePriority: 3,
          checkboxes: true,
          render: function(data, type, full, meta) {
                        return '<div class="form-check"> <input class="form-check-input dt-checkboxes" type="checkbox" value="" id="checkbox' +
                    meta.row + '" /><label class="form-check-label" for="checkbox' +
                    meta.row + '"></label></div>';
                        
                    },
                    checkboxes: {
                        selectAllRender: '<div class="form-check"> <input class="form-check-input" type="checkbox" value="" id="checkboxSelectAll" /><label class="form-check-label" for="checkboxSelectAll"></label></div>'
                    }
        },
        // {
        //   targets: 2,
        //   searchable: false,
        //   visible: false
        // },
    //     {
    //       // Avatar image/badge, Name and post
    //      targets: 3,  // ID column
    // render: function (data, type, full, meta) {
    //   return `<a href="/landlord/listing-dashboard/${data}/" class="text-primary">${data}</a>`;
    // }
    //     },
        {
          responsivePriority: 1,
          targets: 3
        }
      ],
      select: {
        style: 'multi',
        selector: 'td:nth-child(2)'
      },
      order: [[7, 'desc']],
      layout: {
        top2Start: {
          rowClass: 'row card-header flex-column flex-md-row border-bottom mx-0 px-3',
          features: tenantFilters ? [tableTitle, tenantFilters] : [tableTitle]
        },
        top2End: {
          features: [
            {
              buttons: [
                {
                  extend: 'collection',
                  className: 'btn btn-label-primary dropdown-toggle',
                  text: '<span class="d-flex align-items-center gap-2"><i class="icon-base ti tabler-upload icon-xs me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span></span>',
                  buttons: [
                    {
                      extend: 'print',
                      text: `<span class="d-flex align-items-center"><i class="icon-base ti tabler-printer me-1"></i>Print</span>`,
                      className: 'dropdown-item',
                      exportOptions: {
                        columns: [2, 3, 4, 5, 6, 7],
                        format: {
                          body: function (inner, coldex, rowdex) {
                            if (inner.length <= 0) return inner;

                            // Check if inner is HTML content
                            if (inner.indexOf('<') > -1) {
                              const parser = new DOMParser();
                              const doc = parser.parseFromString(inner, 'text/html');

                              // Get all text content
                              let text = '';

                              // Handle specific elements
                              const userNameElements = doc.querySelectorAll('.user-name');
                              if (userNameElements.length > 0) {
                                userNameElements.forEach(el => {
                                  // Get text from nested structure
                                  const nameText =
                                    el.querySelector('.fw-medium')?.textContent ||
                                    el.querySelector('.d-block')?.textContent ||
                                    el.textContent;
                                  text += nameText.trim() + ' ';
                                });
                              } else {
                                // Get regular text content
                                text = doc.body.textContent || doc.body.innerText;
                              }

                              return text.trim();
                            }

                            return inner;
                          }
                        }
                      },
                      customize: function (win) {
                        win.document.body.style.color = config.colors.headingColor;
                        win.document.body.style.borderColor = config.colors.borderColor;
                        win.document.body.style.backgroundColor = config.colors.bodyBg;
                        const table = win.document.body.querySelector('table');
                        table.classList.add('compact');
                        table.style.color = 'inherit';
                        table.style.borderColor = 'inherit';
                        table.style.backgroundColor = 'inherit';
                      }
                    },
                    {
                      extend: 'csv',
                      text: `<span class="d-flex align-items-center"><i class="icon-base ti tabler-file-text me-1"></i>Csv</span>`,
                      className: 'dropdown-item',
                      exportOptions: {
                        columns: [2, 3, 4, 5, 6, 7],
                        format: {
                          body: function (inner, coldex, rowdex) {
                            if (inner.length <= 0) return inner;

                            // Parse HTML content
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(inner, 'text/html');

                            let text = '';

                            // Handle user-name elements specifically
                            const userNameElements = doc.querySelectorAll('.user-name');
                            if (userNameElements.length > 0) {
                              userNameElements.forEach(el => {
                                // Get text from nested structure - try different selectors
                                const nameText =
                                  el.querySelector('.fw-medium')?.textContent ||
                                  el.querySelector('.d-block')?.textContent ||
                                  el.textContent;
                                text += nameText.trim() + ' ';
                              });
                            } else {
                              // Handle other elements (status, role, etc)
                              text = doc.body.textContent || doc.body.innerText;
                            }

                            return text.trim();
                          }
                        }
                      }
                    },
                    {
                      extend: 'excel',
                      text: `<span class="d-flex align-items-center"><i class="icon-base ti tabler-file-spreadsheet me-1"></i>Excel</span>`,
                      className: 'dropdown-item',
                      exportOptions: {
                        columns: [2, 3, 4, 5, 6, 7],
                        format: {
                          body: function (inner, coldex, rowdex) {
                            if (inner.length <= 0) return inner;

                            // Parse HTML content
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(inner, 'text/html');

                            let text = '';

                            // Handle user-name elements specifically
                            const userNameElements = doc.querySelectorAll('.user-name');
                            if (userNameElements.length > 0) {
                              userNameElements.forEach(el => {
                                // Get text from nested structure - try different selectors
                                const nameText =
                                  el.querySelector('.fw-medium')?.textContent ||
                                  el.querySelector('.d-block')?.textContent ||
                                  el.textContent;
                                text += nameText.trim() + ' ';
                              });
                            } else {
                              // Handle other elements (status, role, etc)
                              text = doc.body.textContent || doc.body.innerText;
                            }

                            return text.trim();
                          }
                        }
                      }
                    },
                    {
                      extend: 'pdf',
                      text: `<span class="d-flex align-items-center"><i class="icon-base ti tabler-file-description me-1"></i>Pdf</span>`,
                      className: 'dropdown-item',
                      exportOptions: {
                        columns: [2, 3, 4, 5, 6, 7],
                        format: {
                          body: function (inner, coldex, rowdex) {
                            if (inner.length <= 0) return inner;

                            // Parse HTML content
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(inner, 'text/html');

                            let text = '';

                            // Handle user-name elements specifically
                            const userNameElements = doc.querySelectorAll('.user-name');
                            if (userNameElements.length > 0) {
                              userNameElements.forEach(el => {
                                // Get text from nested structure - try different selectors
                                const nameText =
                                  el.querySelector('.fw-medium')?.textContent ||
                                  el.querySelector('.d-block')?.textContent ||
                                  el.textContent;
                                text += nameText.trim() + ' ';
                              });
                            } else {
                              // Handle other elements (status, role, etc)
                              text = doc.body.textContent || doc.body.innerText;
                            }

                            return text.trim();
                          }
                        }
                      }
                    },
                    {
                      extend: 'copy',
                      text: `<i class="icon-base ti tabler-copy me-1"></i>Copy`,
                      className: 'dropdown-item',
                      exportOptions: {
                        columns: [2, 3, 4, 5, 6, 7],
                        format: {
                          body: function (inner, coldex, rowdex) {
                            if (inner.length <= 0) return inner;

                            // Parse HTML content
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(inner, 'text/html');

                            let text = '';

                            // Handle user-name elements specifically
                            const userNameElements = doc.querySelectorAll('.user-name');
                            if (userNameElements.length > 0) {
                              userNameElements.forEach(el => {
                                // Get text from nested structure - try different selectors
                                const nameText =
                                  el.querySelector('.fw-medium')?.textContent ||
                                  el.querySelector('.d-block')?.textContent ||
                                  el.textContent;
                                text += nameText.trim() + ' ';
                              });
                            } else {
                              // Handle other elements (status, role, etc)
                              text = doc.body.textContent || doc.body.innerText;
                            }

                            return text.trim();
                          }
                        }
                      }
                    }
                  ]
                },
                {
                  text: '<span class="d-flex align-items-center gap-2"><i class="icon-base ti tabler-plus icon-sm"></i> <span class="d-none d-sm-inline-block">Add New Tenant</span></span>',
                  className: 'create-new btn btn-primary',
                  action: function (e, dt, node, config) {
                        window.location.href = '/landlord/tenant-add';
                    }
                }
              ]
            }
          ]
        },
        topStart: {
          rowClass: 'row mx-0 px-3 my-0 justify-content-between border-bottom',
          features: []
        },
        topEnd: { features: [] },
        bottomStart: {
          rowClass: 'row mx-3 justify-content-between',
          features: ['info']
        },
        bottomEnd: 'paging'
      },
      language: {
        paginate: {
          next: '<i class="icon-base ti tabler-chevron-right scaleX-n1-rtl icon-18px"></i>',
          previous: '<i class="icon-base ti tabler-chevron-left scaleX-n1-rtl icon-18px"></i>',
          first: '<i class="icon-base ti tabler-chevrons-left scaleX-n1-rtl icon-18px"></i>',
          last: '<i class="icon-base ti tabler-chevrons-right scaleX-n1-rtl icon-18px"></i>'
        }
      },
      responsive: {
        details: {
          display: DataTable.Responsive.display.modal({
            header: function (row) {
              const data = row.data();
              return 'Details of ' + data['full_name'];
            }
          }),
          type: 'column',
          renderer: function (api, rowIdx, columns) {
            const data = columns
              .map(function (col) {
                return col.title !== '' // Do not show row in modal popup if title is blank (for check box)
                  ? `<tr data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}">
                      <td>${col.title}:</td>
                      <td>${col.data}</td>
                    </tr>`
                  : '';
              })
              .join('');

            if (data) {
              const div = document.createElement('div');
              div.classList.add('table-responsive');
              const table = document.createElement('table');
              div.appendChild(table);
              table.classList.add('table');
              table.classList.add('datatables-basic');
              const tbody = document.createElement('tbody');
              tbody.innerHTML = data;
              table.appendChild(tbody);
              return div;
            }
            return false;
          }
        }
      }
    });

    const propertyInputs = Array.from(document.querySelectorAll('.property-filter-checkbox'));
    const propertyLabel = document.getElementById('propertyFilterLabel');
    const rentDueFilter = document.getElementById('rentDueFilter');
    const tenantNameSearch = document.getElementById('tenantNameSearch');
    const selectedProperties = () => propertyInputs.filter(input => input.checked).map(input => String(input.value));

    function refreshPropertyLabel() {
      const selected = propertyInputs.filter(input => input.checked);
      rentDueFilter.disabled = selected.length === 0;
      if (!selected.length) {
        propertyLabel.textContent = 'All properties';
        rentDueFilter.value = 'all';
      } else if (selected.length === 1) {
        propertyLabel.textContent = selected[0].nextElementSibling.textContent.trim();
      } else {
        propertyLabel.textContent = `${selected.length} properties selected`;
      }
    }

    DataTable.ext.search.push(function (settings, data, dataIndex, rowData) {
      if (settings.nTable !== dt_basic_table) return true;
      const selected = selectedProperties();
      const propertyMatches = selected.length === 0 || selected.includes(String(rowData.property_id));
      const dueMatches = rentDueFilter.value !== 'due' || rowData.rent_due === true;
      const query = tenantNameSearch.value.trim().toLocaleLowerCase();
      const nameMatches = !query || String(rowData.full_name || '').toLocaleLowerCase().includes(query);
      return propertyMatches && dueMatches && nameMatches;
    });

    propertyInputs.forEach(input => input.addEventListener('change', () => {
      refreshPropertyLabel();
      dt_basic.draw();
    }));
    document.querySelector('.tenant-property-menu')?.addEventListener('click', event => event.stopPropagation());
    document.getElementById('clearPropertyFilter')?.addEventListener('click', () => {
      propertyInputs.forEach(input => { input.checked = false; });
      refreshPropertyLabel();
      dt_basic.draw();
    });
    rentDueFilter.addEventListener('change', () => dt_basic.draw());
    tenantNameSearch.addEventListener('input', () => dt_basic.draw());
    refreshPropertyLabel();

    // Add New record
    // ? Remove/Update this code as per your requirements
  

    //? The 'delete-record' class is necessary for the functionality of the following code.
    document.addEventListener('click', function (e) {
      if (e.target.classList.contains('delete-record')) {
        dt_basic.row(e.target.closest('tr')).remove().draw();
        const modalEl = document.querySelector('.dtr-bs-modal');
        if (modalEl && modalEl.classList.contains('show')) {
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal?.hide();
        }
      }
    });
  }



  // Filter form control to default size
  // ? setTimeout used for multilingual table initialization
  setTimeout(() => {
    const elementsToModify = [
      { selector: '.dt-buttons .btn', classToRemove: 'btn-secondary' },
      { selector: '.dt-search .form-control', classToRemove: 'form-control-sm', classToAdd: 'ms-4' },
      { selector: '.dt-length .form-select', classToRemove: 'form-select-sm' },
      { selector: '.dt-layout-table', classToRemove: 'row mt-2' },
      { selector: '.dt-layout-end', classToAdd: 'mt-0' },
      { selector: '.dt-layout-end .dt-search', classToAdd: 'mt-0 mt-md-6 mb-6' },
      { selector: '.dt-layout-start', classToAdd: 'mt-0' },
      { selector: '.dt-layout-end .dt-buttons', classToAdd: 'mb-0' },
      { selector: '.dt-layout-full', classToRemove: 'col-md col-12', classToAdd: 'table-responsive' }
    ];

    // Delete record
    elementsToModify.forEach(({ selector, classToRemove, classToAdd }) => {
      document.querySelectorAll(selector).forEach(element => {
        if (classToRemove) {
          classToRemove.split(' ').forEach(className => element.classList.remove(className));
        }
        if (classToAdd) {
          classToAdd.split(' ').forEach(className => element.classList.add(className));
        }
      });
    });
  }, 100);
});
