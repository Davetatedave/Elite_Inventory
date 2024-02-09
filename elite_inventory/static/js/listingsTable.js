let quantityCounter = function (data, type, row) {
  return `<div class="adjust">
	<button class="minus btn btn-sm btn-dark">-</button>
	<input readonly class="adjustInput" type="text" value="0" data-stock_listed=${row.stock_listed} data-stock_available=${row.stock_available}>
	<button class="plus btn btn-sm btn-dark">+</button>
  <button data-id="${row.listing_id}" class="add btn btn-primary">Update</button>
</div>`;
};

$(document).ready(function () {
  let bmTable = $("#BMlistings").DataTable({
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
      url: "/BMlistingsajax/",
      data: function (d) {
        return $.extend({}, d, { macs: $("#macToggle").is(":checked") });
      },
      dataSrc: "data", // Data property name in the JSON response
    },
    columns: [
      {
        data: "SKU",
        render: function (data, type, row, meta) {
          return data != null
            ? '<a href="detail/' + row.pk + '">' + data + "</a>"
            : '<a href="resolve_marketplace_sku/' +
                row.listing_id +
                '">' +
                "Resolve SKU" +
                "</a>"; // Replace 'Not specified' with any default or placeholder text
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
        data: "stock_listed",
        orderable: false,
        render: function (data, type, row) {
          return data ? data : 0; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        data: "stock_available",
        orderable: false,
        render: function (data, type, row) {
          return data ? data : 0; // Replace 'Not specified' with any default or placeholder text
        },
      },
      {
        name: "quantityAdjust",
        orderable: false,
        render: function (data, type, row) {
          return quantityCounter(data, type, row);
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
  bmTable.on("init.dt", function () {
    let intervalId;
    $(document).on("mousedown", ".plus", function () {
      let input = $(this).siblings("input");
      let currentValue = parseInt(input.val(), 10);
      let stockListed = parseInt(input.data("stock_listed"), 10);
      let stockAvailable = parseInt(input.data("stock_available"), 10);
      let max = stockAvailable - stockListed; // Assuming minimum is 0 or another positive number

      // Decrement the value on initial mousedown
      if (currentValue < max) {
        input.val(currentValue + 1);
      } else {
        // Stop the continuous decrement when reaching the minimum
        clearInterval(intervalId);
        showTooltip(input, "Max Amount");
      }

      // Set up a continuous decrement while mouse is held down
      intervalId = setInterval(function () {
        let currentValue = parseInt(input.val(), 10);

        if (currentValue < max) {
          input.val(currentValue + 1);
        } else {
          // Stop the continuous decrement when reaching the minimum
          clearInterval(intervalId);
          showTooltip(input, "Max Amount");
        }
      }, 100); // Adjust the interval time (in milliseconds) as needed
    });
    $(document).on("mouseup", ".plus", function () {
      clearInterval(intervalId);
    });
    $(document).on("mousedown", ".minus", function () {
      let input = $(this).siblings("input");
      let currentValue = parseInt(input.val(), 10);
      let stockListed = parseInt(input.data("stock_listed"), 10);
      let min = -stockListed; // Assuming minimum is 0 or another positive number

      // Decrement the value on initial mousedown
      if (currentValue > min) {
        input.val(currentValue - 1);
      } else {
        // Stop the continuous decrement when reaching the minimum
        clearInterval(intervalId);
        showTooltip(input, "Min Amount");
      }

      // Set up a continuous decrement while mouse is held down
      intervalId = setInterval(function () {
        let currentValue = parseInt(input.val(), 10);

        if (currentValue > min) {
          input.val(currentValue - 1);
        } else {
          // Stop the continuous decrement when reaching the minimum
          clearInterval(intervalId);
          showTooltip(input, "Min Amount");
        }
      }, 100); // Adjust the interval time (in milliseconds) as needed
    });
    $(document).on("mouseup", ".minus", function () {
      clearInterval(intervalId);
    });
    $(document).on("click", ".add", function () {
      console.log("Add clicked");
      let csrftoken = Cookies.get("csrftoken");
      let listing_id = $(this).data("id");
      let input = $(this).siblings("input");
      let currentValue = parseInt(input.val(), 10);
      let stockListed = parseInt(input.data("stock_listed"), 10);
      let data = {
        listing_id: listing_id,
        quantity: currentValue + stockListed,
      };
      $.ajax({
        type: "POST",
        url: "/updateBMquantity/",
        headers: { "X-CSRFToken": csrftoken },
        data: data,
        success: function (result) {
          console.log(result);
          bmTable.ajax.reload();
        },
      });
    });
  });
});
