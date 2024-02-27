$("#shipperSelect").select2({
  placeholder: "Select a Shipper",
  theme: "classic",
});

// Sales Table
$(document).ready(function () {
  let salesTable = $("#salesTable").DataTable({
    order: [],
    scrollX: true,
    dom: "Bfrtip",
    buttons: [
      "pageLength",
      {
        text: "Get Pick List",
        action: function () {
          window.open("/getPickList/", "_blank");
        },
      },
    ],

    ajax: {
      url: "/salesajax/",
      data: function (d) {
        return $.extend({}, d, {
          channel: $("#channelFilter").val(),
          status: $("#statusFilter").val(),
          success: function (response) {},
        });
      },
      dataSrc: "data", // Data property name in the JSON response
    },
    columns: [
      {
        data: "order_id",
        render: function (data, type, row, meta) {
          return (
            '<button hx-get="/sales/detail/' +
            row.pk +
            '" hx-target="#modals-here" hx-trigger="click" @click="modalShow = !modalShow" class="btn btn-primary">' +
            row.order_id +
            "</button>"
          );
        },
        orderable: false,
      },
      {
        data: "order_date",
        orderable: false,
        render: function (data, type, row) {
          return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "channel",
        orderable: false,
        render: function (data, type, row) {
          return data ? data : 0; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "customer",
        orderable: false,
        render: function (data, type, row) {
          return data ? data : 0; // Replace 'Not specified' with any default or placeholder text
        },
      },
      { data: "quantity", orderable: false },
      {
        data: "state",
        orderable: false,
        render: function (data, type, row) {
          return data
            ? data == "Shipped"
              ? '<button class="btn btn-success shipped">' + data + "</button>"
              : data
            : Unknown; // Replace 'Not specified' with any default or placeholder text
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
    searching: true,
  });
  $(".filter").on("change", function () {
    salesTable.ajax.reload(function () {
      htmx.process(document.body);
    });
  });
  salesTable.on("init.dt", function () {
    let url = new URL(window.location.href);
    let so_search = url.searchParams.get("so");
    let so_id = url.searchParams.get("so_id");
    if (so_search) {
      $("#statusFilter").val("Shipped");
      salesTable.search(so_search).draw();

      reloadModal(so_id);
    }

    htmx.process(document.body);
  });
});

// After Modal Load
document.addEventListener("htmx:afterRequest", function (evt) {
  if (evt.detail.target.id === "modals-here") {
    initialiseModal();
  }
});

//Reload Modal
function reloadModal(so_id) {
  if (so_id == undefined) {
    var so_id = $("#order").data("so");
  }
  $.ajax({
    url: "./detail/" + so_id,
    success: function (response) {
      $("#modals-here").html(response);
      initialiseModal();
    },
  });
}
