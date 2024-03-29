// DataTables

///Available Statuses for Change Status Button
var statusdata = JSON.parse(
  document.getElementById("filter_body").getAttribute("data-status")
);

var grades = JSON.parse(
  document.getElementById("filter_body").getAttribute("data-grades")
);
// Create an array of button configurations
var statusButtons = statusdata.map(function (item) {
  return {
    text: item.fields.status, // Assuming 'status' is a property of 'fields' in each 'item'
    action: function (e, dt, node, config) {
      var csrftoken = Cookies.get("csrftoken");
      var selectedRows = dt.rows({ selected: true });
      var soldDevices = [];
      var selectedPKs = [];
      selectedRows.data().each(function (row) {
        if (row.status != "Sold") {
          selectedPKs.push(row.pk);
        } else {
          soldDevices.push(row.imei);
        }
      });
      if (soldDevices.length > 0 && soldDevices.length < 11) {
        alert(
          "The following devices are already sold: " +
            soldDevices.join(", ") +
            "\nRemove them from POs to update status."
        );
      }
      if (soldDevices.length > 10) {
        alert("Cannot Update Status of Sold Devices. Remove them from POs");
      }
      console.log(selectedPKs);
      // Send all selected PKs in a single request
      $.ajax({
        url: "/updateStatus/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        data: {
          pks: selectedPKs,
          status: item.pk,
        },
        success: function (response) {
          console.log(response.message);

          setTimeout(function () {
            dt.ajax.reload();
          }, 200); // Adjust the delay duration as needed
        },
        traditional: true,
      });
    },
  };
});

var gradeButtons = grades.map(function (item) {
  return {
    text: item,
    action: function (e, dt, node, config) {
      var csrftoken = Cookies.get("csrftoken");
      var selectedRows = dt.rows({ selected: true });
      var selectedPKs = selectedRows.data().map((row) => row.pk);
      // Send all selected PKs in a single request
      $.ajax({
        url: "/updateGrade/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        data: {
          pks: selectedPKs.toArray(),
          grade: item,
        },
        success: function (response) {
          console.log(response.message);

          setTimeout(function () {
            dt.ajax.reload();
          }, 200); // Adjust the delay duration as needed
        },
        error: function (response) {
          console.log(response.responseJSON);
          alert(response.responseJSON.message);
        },
        traditional: true,
      });
    },
  };
});

$.fn.dataTable.ext.buttons.changeStatus = {
  extend: "collection",
  text: "Change Status",
  buttons: statusButtons,
};

$.fn.dataTable.ext.buttons.changeGrade = {
  extend: "collection",
  text: "Change Grade",
  buttons: gradeButtons,
};

// Function to get the IDs or values of all checked switches
function getCheckedGroupSwitches() {
  var grouping = [];
  $(".form-check-input:checked").each(function () {
    grouping.push($(this).val());
  });
  console.log(grouping);
  return grouping;
}

function toggleEdit(selectedRows) {
  // Iterate over each selected row
  selectedRows.every(function (rowIdx, tableLoop, rowLoop) {
    var $row = $(this.node()); // Get the jQuery object for the current row
    $row.addClass("table-warning"); // Highlight the row
    // For each row, find the SKU input and related elements
    var $input = $row.find(".sku-input");
    var $editBtn = $row.find(".edit-sku");
    var $submitBtn = $row.find(".submit-sku");

    // Make the SKU inputs editable
    $input.prop("readonly", false);

    // Initially hide the submit button until a change is made
    $submitBtn.addClass("d-none");

    // Attach a change event listener to the SKU input to detect changes
    $input.off("input.toggleEdit").on("input.toggleEdit", function () {
      // When input value changes, show the corresponding submit button
      $submitBtn.removeClass("d-none");
    });
  });
  selectedRows.deselect(); // Deselect all rows after toggling edit mode
}

// Assuming '.submit-sku' buttons are inside DataTable rows and use delegated event binding for dynamic elements
$(document).on("click", ".submit-sku", function () {
  var $currentTd = $(this).closest("td");
  var newSKU = $currentTd.find(".sku-input").val();

  var tdIndex = $currentTd.index();

  // Select the next four <td> elements after the current <td>
  var deviceInfo = $currentTd
    .closest("tr")
    .find("td")
    .slice(tdIndex + 1, tdIndex + 5)
    .map(function () {
      return $(this).text(); // Or adjust based on where the data is within the <td>
    })
    .get();

  $.ajax({
    url: "/updateSKU/",
    type: "POST",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
    data: {
      new_sku: newSKU,
      deviceInfo: deviceInfo,
    },
    success: function (response) {
      alert(response.message); // Or handle the success case more gracefully
      table.ajax.reload(null, false); // Reload the table data without resetting the paging
    },
    error: function (xhr, status, error) {
      showTooltip($currentTd, xhr.responseJSON.error);
      console.log(xhr.responseJSON);
      // Optionally, display an error message
    },
  });
});

var batterySlider = $(function () {
  $("#slider-range").slider({
    range: true,
    min: 0,
    max: 100,
    values: [0, 100],
    slide: function (event, ui) {
      $("#amount").val(ui.values[0] + "-" + ui.values[1]);
    },
  });
  $("#amount").val(
    $("#slider-range").slider("values", 0) +
      "-" +
      $("#slider-range").slider("values", 1)
  );
});

function initialiseTable(grouping = getCheckedGroupSwitches()) {
  var invTable = $("#invTable").DataTable({
    order: [],
    scrollX: true,
    dom: "Bfrtip",
    buttons: [
      "pageLength",
      "selectAll",
      "changeStatus",
      "changeGrade",
      {
        text: "Edit SKUs",
        action: function (e, dt, node, config) {
          var selectedRows = dt.rows({ selected: true });
          console.log(selectedRows);
          toggleEdit(selectedRows);
        },
      },
      {
        text: "Delete",
        action: function (e, dt, node, config) {
          if (window.confirm("Really Delete Rows?")) {
            var csrftoken = Cookies.get("csrftoken");
            console.log("csrftoken: " + csrftoken);
            var selectedRows = dt.rows({ selected: true });
            let selectedPKs = selectedRows.data().map((row) => row.pk);

            $.ajax({
              url: "/deletedevices/",
              type: "POST",
              headers: { "X-CSRFToken": csrftoken },
              data: {
                pks: selectedPKs.toArray(),
              },
              success: function (response) {
                console.log(response.message);

                setTimeout(function () {
                  dt.ajax.reload();
                }, 200); // Adjust the delay duration as needed
              },
              traditional: true,
            });
          } else {
            console.log("cancel");
          }
        },
      },
      {
        extend: "excel",
        text: "Export",
        title: "Inventory Report",
        exportOptions: { columns: ":visible" },
      },
    ],

    ajax: {
      url: "/inventoryajax/", // Replace with your Django view URL
      data: function (d) {
        return $.extend({}, d, {
          model: $("#modelSelect").val(),
          capacity: $("#capacitySelect").val(),
          grade: $("#gradeSelect").val(),
          color: $("#colorSelect").val(),
          status: $("#statusSelect").val(),
          batteryA: $("#slider-range").slider("values", 0),
          batteryB: $("#slider-range").slider("values", 1),
          bulk_search_value: $("#bulkImeiInput").val(),
          grouping: grouping,
        });
      },
      error: function (xhr) {
        showTooltip($("#bulkImeiInput"), xhr.responseJSON.error);
      },
      dataSrc: "data", // Data property name in the JSON response
    },
    columns: [
      {
        data: "imei",
        render: function (data, type, row, meta) {
          return '<a href="detail/' + row.pk + '">' + data + "</a>";
        },
        visible: grouping.length === 0,
        orderable: false,
      },
      {
        data: "sku",
        render: function (data, type, row, meta) {
          return `
              <div class="input-group">
                  <input type="text" class="form-control sku-input" readonly value="${
                    data ? data : "Missing"
                  }" data-pk="${row.pk}" />
                  <button class="btn btn-primary submit-sku d-none" type="button">Update</button>
              </div>
          `;
        },
        visible: grouping.length === 0,
        orderable: false,
      },
      {
        data: "model",
        visible: grouping.includes("model") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "capacity",
        visible: grouping.includes("capacity") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "color",
        visible: grouping.includes("color") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "grade",
        visible: grouping.includes("grade") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Ungraded"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "battery",
        visible: grouping.length === 0,
        orderable: true,
        render: function (data, type, row) {
          return data ? data : "N/A"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "status",
        visible: grouping.includes("status") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data
            ? data == "Sold"
              ? '<a href="/sales/?so=' +
                row.so +
                "&so_id=" +
                row.so_id +
                '"class="btn btn-primary">Sold</a>'
              : data
            : "N/A"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "count",
        visible: grouping.length > 0,
        orderable: true,
        render: function (data, type, row) {
          return data ? data : Null; // Replace 'Not specified' with any default or placeholder text
        },
      },
    ],
    lengthMenu: [
      [10, 25, 50, -1],
      [10, 25, 50, "All"],
    ], // Define the dropdown menu options for record per page
    pageLength: 10,
    processing: true,
    serverSide: true,
    select: true,
    language: {
      searchPlaceholder: "Search by IMEI or SKU",
    },
  });
  return invTable;
}

$(document).ready(function () {
  $("#modelSelect").select2({
    placeholder: "Select Models",
    theme: "classic",
  });
  $("#capacitySelect").select2({
    placeholder: "Select Capacity",
    theme: "classic",
  });
  $("#colorSelect").select2({
    placeholder: "Select Colors",
    theme: "classic",
  });
  $("#gradeSelect").select2({
    placeholder: "Select Grades",
    theme: "classic",
  });
  $("#statusSelect").select2({
    placeholder: "Select Statuses",
    theme: "classic",
  });

  var invTable = initialiseTable();

  // Event listener for filter
  $(".filter").on("change", function () {
    // Reload DataTable with new filter criteria
    if ($(".form-check-input:checked").length > 0) {
      if ($.fn.DataTable.isDataTable("#invTable")) {
        $("#invTable").DataTable().destroy();
        console.log("destroy");
      }
      initialiseTable();
    } else {
      invTable.ajax.reload();
      console.log("reload");
    }
  });

  batterySlider.on("slidechange", function (event, ui) {
    $("#invTable").DataTable().destroy();
    console.log("destroy");

    initialiseTable();
  });

  // Attach a change event listener to the switches
  $(".form-check-input").on("change", function () {
    // Reload DataTable with new grouping
    if ($.fn.DataTable.isDataTable("#invTable")) {
      $("#invTable").DataTable().destroy();
      console.log("destroy");
    }
    initialiseTable();
  });
});
