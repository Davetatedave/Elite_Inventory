// DataTables

//TODO: Add a button to change status of selected rows

$.fn.dataTable.ext.buttons.changeStatus = {
  extend: "collection",
  text: "Change Status",
  buttons: [
    {
      text: "Sold",
      action: function (e, dt, node, config) {
        var csrftoken = Cookies.get("csrftoken");
        var selectedRows = dt.rows({ selected: true });
        let selectedPKs = selectedRows.data().map((row) => row.pk);
        selectedPKs.each(function (value) {
          console.log("Sold:" + value);
        });
      },
    },
  ],
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
          grade: $("#gradeSelect").val(),
          color: $("#colorSelect").val(),
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
});
