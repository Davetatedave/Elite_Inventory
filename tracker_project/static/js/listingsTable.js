let quantityCounter = function (data, type, row) {
  return `<div class="adjust">
	<button class="minus btn btn-sm btn-dark">-</button>
	<input readonly class="adjustInput" type="text" value="0" data-stock_listed=${row.stock_listed} data-stock_available=${row.stock_available}>
	<button class="plus btn btn-sm btn-dark">+</button>
  <button class="add btn btn-primary">Update</button>
</div>`;
};

function showTooltip(element, message) {
  let tooltip = $(".tooltip-custom");

  if (!tooltip.length) {
    // Create tooltip if it doesn't exist
    tooltip = $('<div class="tooltip-custom"></div>').appendTo("body");
  }

  tooltip.text(message);
  let elementOffset = element.offset();
  tooltip.css({
    top: elementOffset.top - tooltip.outerHeight() - 10,
    left: elementOffset.left,
  });

  tooltip.stop().fadeIn(150);

  // Hide tooltip after some time (optional)
  setTimeout(function () {
    tooltip.fadeOut();
  }, 3000);
}

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
        data: "buyboxes",
        orderable: false,
        render: function (data, type, row) {
          return "<a href='/buyboxes/" + row.pk + "'>" + data + "</a>";
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
    $(".plus")
      .on("mousedown", function () {
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
      })
      .on("mouseup", function () {
        clearInterval(intervalId); // Stop the continuous decrement on mouseup
      });

    $(".minus")
      .on("mousedown", function () {
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
      })
      .on("mouseup", function () {
        clearInterval(intervalId); // Stop the continuous decrement on mouseup
      });
  });
});
