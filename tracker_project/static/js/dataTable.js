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
        // TODO: Implement Deletion Logic. I will probably 'delete' using flags rather than remove row.
        text: "Delete",
        action: function () {
          if (window.confirm("Really Delete Rows?")) {
            let selectedRows = invTable.rows({ selected: true });
            selectedRows.every(function () {
              let row = this.data();
              console.log(row.imei + " Deleted");
            });
          } else {
            console.log("cancel");
          }
        },
      },
    ],

    ajax: {
      url: "/inventoryAjax/", // Replace with your Django view URL
      data: function () {
        return {
          model: $("#statusFilter").val(),
        };
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
