// DataTables

///Available Statuses for Change Status Button
var statusdata = JSON.parse(
  document.getElementById("filter_body").getAttribute("data-filter-data")
);

// Create an array of button configurations
var buttonConfigs = statusdata.map(function (item) {
  return {
    text: item.fields.status, // Assuming 'status' is a property of 'fields' in each 'item'
    action: function (e, dt, node, config) {
      var csrftoken = Cookies.get("csrftoken");
      var selectedRows = dt.rows({ selected: true });
      let selectedPKs = selectedRows.data().map((row) => row.pk);
      console.log(item.pk);
      selectedPKs.each(function (value) {
        $.ajax({
          url: "/updateStatus/",
          type: "POST",
          headers: { "X-CSRFToken": csrftoken },
          data: {
            pks: selectedPKs.toArray(),
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
        console.log(item.fields.status + "=" + value);
        // Additional logic for each button
      });
    },
  };
});

$.fn.dataTable.ext.buttons.changeStatus = {
  extend: "collection",
  text: "Change Status",
  buttons: buttonConfigs,
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

function initialiseTable(grouping = getCheckedGroupSwitches()) {
  var invTable = $("#invTable").DataTable({
    order: [],
    dom: "Bfrtip",
    buttons: [
      "colvis",
      "pageLength",
      "selectAll",
      "selectNone",
      "changeStatus",
      {
        text: "Delete",
        action: function () {
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
    ],

    ajax: {
      url: "/inventoryajax/", // Replace with your Django view URL
      data: function (d) {
        return $.extend({}, d, {
          model: $("#modelSelect").val(),
          grade: $("#gradeSelect").val(),
          color: $("#colorSelect").val(),
          batteryA: $("#battAb").val(),
          batteryB: $("#battBe").val(),
          grouping: grouping,
        });
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
        data: "model",
        visible: grouping.includes("model") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "capacity",
        visible: grouping.includes("capacity") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "color",
        visible: grouping.includes("color") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "grade",
        visible: grouping.includes("grade") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "battery",
        visible: grouping.length === 0,
        orderable: true,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "status",
        visible: grouping.includes("status") || grouping.length === 0,
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "count",
        visible: grouping.length > 0,
        orderable: true,
        render: function (data, type, row) {
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
        },
      },
    ],
    lengthMenu: [10, 25, 50], // Define the dropdown menu options for record per page
    pageLength: 10,
    processing: true,
    serverSide: true,
    select: true,
  });
  return invTable;
}

$(document).ready(function () {
  $("#modelSelect").select2({
    placeholder: "Select Models",
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
    console.log("Status Changed");
    console.log($("#gradeSelect").val());
    console.log($("#modelSelect").val());
    if ($.fn.DataTable.isDataTable("#invTable")) {
      $("#invTable").DataTable().destroy();
    }
    initialiseTable();
  });

  // Attach a change event listener to the switches
  $(".form-check-input").on("change", function () {
    // Reload DataTable with new grouping
    if ($.fn.DataTable.isDataTable("#invTable")) {
      $("#invTable").DataTable().destroy();
    }
    initialiseTable();
  });
});
