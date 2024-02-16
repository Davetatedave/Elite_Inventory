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
      var selectedPKs = selectedRows.data().map((row) => row.pk);
      // Send all selected PKs in a single request
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
      "selectNone",
      "changeStatus",
      "changeGrade",
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
          return data ? data : "Not specified"; // Replace 'Not specified' with any default or placeholder text
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
