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
          grouping: getCheckedGroupSwitches(),
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
        orderable: false,
      },
      { data: "model", orderable: false },
      { data: "capacity", orderable: false },
      { data: "color", orderable: false },
      { data: "grade" },
      { data: "battery", orderable: true },
      { data: "status", orderable: false },
    ],
    lengthMenu: [10, 25, 50], // Define the dropdown menu options for record per page
    pageLength: 10,
    processing: true,
    serverSide: true,
    select: true,
  });

  // Event listener for filter
  $(".filter").on("change", function () {
    // Reload DataTable with new filter criteria
    console.log("Status Changed");
    console.log($("#gradeSelect").val());
    console.log($("#modelSelect").val());
    invTable.ajax.reload();
  });
  // Function to get the IDs or values of all checked switches
  function getCheckedGroupSwitches() {
    var grouping = [];
    $(".form-check-input:checked").each(function () {
      grouping.push($(this).val());
    });
    return grouping;
  }

  // Attach a change event listener to the switches
  $(".form-check-input").on("change", function () {
    var checked = getCheckedGroupSwitches();
    console.log(checked);
    invTable.ajax.reload();
  });
});
