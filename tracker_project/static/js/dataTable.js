// DataTables

$(document).ready(function () {
  var invTable = $("#invTable").DataTable({
    order: [],
    dom: "Bfrtip",
    buttons: [
      "colvis",
      "pageLength",
      "selectAll",
      "selectNone",
      {
        text: "Delete",
        action: function (e, dt, node, config) {
          if (window.confirm("Really Delete Rows?")) {
            var csrftoken = Cookies.get("csrftoken");
            var selectedRows = dt.rows({ selected: true });
            let selectedPKs = selectedRows.data().map((row) => row.pk);
            selectedRows.remove().draw(false);
            console.log(selectedPKs.toArray());
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
          model: $("#statusFilter").val(),
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
  $("#statusFilter").on("change", function () {
    // Reload DataTable with new filter criteria
    console.log("Status Changed");
    invTable.ajax.reload();
  });
});
