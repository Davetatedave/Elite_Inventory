$(document).ready(function () {
  let salesTable = $("#salesTable").DataTable({
    order: [],
    scrollX: true,
    dom: "Bfrtip",
    buttons: [
      "pageLength",
      {
        text: "Get New Data",
        action: function () {
          $.ajax({
            url: "/getBMdata/",
            success: function (result) {
              console.log("Got BM Data:" + result.response);
            },
          });
        },
      },
    ],

    ajax: {
      url: "/salesajax/",
      data: function (d) {
        return $.extend({}, d, {
          // ADD YOUR PARAMETERS HERE
        });
      },
      dataSrc: "data", // Data property name in the JSON response
    },
    columns: [
      {
        data: "order_id",
        render: function (data, type, row, meta) {
          return (
            '<button hx-get="./detail/' +
            row.order_id +
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
          return data ? data : Unknown; // Replace 'Not specified' with any default or placeholder text
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
    searching: false,
  });
  salesTable.on("init.dt", function () {
    htmx.process(document.body);
  });
});
