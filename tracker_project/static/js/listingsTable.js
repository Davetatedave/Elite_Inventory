$("#BMlistings").DataTable({
  order: [],
  scrollX: true,
  dom: "Bfrtip",
  buttons: ["pageLength"],

  ajax: {
    url: "/BMlistingsajax/", // Replace with your Django view URL
    dataSrc: "data", // Data property name in the JSON response
  },
  columns: [
    {
      data: "SKU",
      render: function (data, type, row, meta) {
        return '<a href="detail/' + row.pk + '">' + data + "</a>";
      },
      orderable: false,
    },
    {
      data: "product_name",
      orderable: false,
      render: function (data, type, row) {
        return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
      },
    },
    {
      data: "price",
      orderable: false,
      render: function (data, type, row) {
        return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
      },
    },
    {
      data: "stock_listed",
      orderable: false,
      render: function (data, type, row) {
        return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
      },
    },
    {
      data: "stock_available",
      orderable: false,
      render: function (data, type, row) {
        return data ? data : "Missing"; // Replace 'Not specified' with any default or placeholder text
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
