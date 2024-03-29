$("#managetoggle").on("change", function () {
  console.log("Toggle clicked:" + $(this).prop("checked"));
  let csrftoken = Cookies.get("csrftoken");
  $.ajax({
    type: "POST",
    url: "/listings/",
    headers: { "X-CSRFToken": csrftoken },
    data: { manage: $(this).prop("checked") },
    success: function (result) {
      console.log(result);
    },
  });
});

let quantityCounter = function (data, type, row, marketplace) {
  return `<div class="adjust">
	<button class="minus${marketplace} btn btn-sm btn-dark">-</button>
	<input readonly class="adjustInput" type="text" value="0" data-stock_listed=${row.stock_listed} data-stock_available=${row.stock_available}>
	<button class="plus${marketplace} btn btn-sm btn-dark">+</button>
  <button data-id="${row.listing_id}" class="add${marketplace} btn btn-primary">Update</button>
</div>`;
};

$(document).ready(function () {
  $.ajax({
    method: "GET",
    url: "/listings/",
    data: {
      marketplace: $("#marketplaceSelect .nav-link.active").data("value"),
    },
    success: function (result) {
      $("#marketplacetabcontainer").html(result.html);
      initialiseTable();
    },
  });
});

$("#marketplaceSelect .nav-link").on("click", function () {
  clicked = $(this);
  active = $("#marketplaceSelect .nav-link.active");
  if (clicked.data("value") == active.data("value")) {
    return;
  }
  active.removeClass("active");
  clicked.addClass("active");

  $.ajax({
    method: "GET",
    url: "/listings/",
    data: {
      marketplace: clicked.data("value"),
    },
    success: function (result) {
      $("#marketplacetabcontainer").html(result.html);
      initialiseTable();
    },
  });
});

let initialiseTable = function () {
  if ($("#marketplaceSelect .nav-link.active").data("value") == "BM") {
    const getBmData = function () {
      $.ajax({
        url: "/getBMdata/",
        success: function (result) {
          console.log("Got BM Data:" + result.response);
          bmTable.ajax.reload();
        },
      });
    };

    let bmTable = $("#BMlistings").DataTable({
      order: [],
      scrollX: true,
      dom: "Bfrtip",
      buttons: [
        "pageLength",
        {
          text: "Get New Data",
          action: getBmData,
        },
      ],

      ajax: {
        url: "/BMlistingsajax/",
        dataSrc: "data", // Data property name in the JSON response
      },
      columns: [
        {
          data: "SKU",
          render: function (data, type, row, meta) {
            return data != null
              ? '<a href="detail/' + row.listing_id + '">' + data + "</a>"
              : '<a  href="/edit_sku/" class="btn btn-warning">{{row.}}</a>';
          },
          orderable: false,
        },
        {
          data: "product_name",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : "Missing Title on BM";
          },
        },
        {
          data: "stock_listed",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : 0;
          },
        },
        {
          data: "stock_available",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : 0;
          },
        },
        {
          name: "quantityAdjust",
          orderable: false,
          render: function (data, type, row) {
            return quantityCounter(data, type, row, (marketplace = "BM"));
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
      htmx.process(document.body);
      let intervalId;
      $(document).on("mousedown", ".plusBM", function () {
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
      $(document)
        .off("mouseup", ".plusBM")
        .on("mouseup", ".plusBM", function () {
          clearInterval(intervalId);
        });
      $(document)
        .off("mousedown", ".minusBM")
        .on("mousedown", ".minusBM", function () {
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
      $(document)
        .off("mouseup", ".minusBM")
        .on("mouseup", ".minusBM", function () {
          clearInterval(intervalId);
        });
      $(document)
        .off("click", ".addBM")
        .on("click", ".addBM", function () {
          if ($("#marketplaceSelect .nav-link.active") == "BM") {
            console.log("Add BM");
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
                getBmData();
              },
            });
          } else {
            return;
          }
        });
    });
  } else {
    console.log("RE Table");
    const getReData = function () {
      console.log("Getting RE Data");
      $.ajax({
        url: "/getREdata/",
        success: function (result) {
          console.log("Got RE Data:" + result.response);
          reTable.ajax.reload();
        },
      });
    };
    let reTable = $("#RElistings").DataTable({
      order: [],
      scrollX: true,
      dom: "Bfrtip",
      buttons: ["pageLength"],

      ajax: {
        url: "/RElistingsajax/",
        dataSrc: "data", // Data property name in the JSON response
      },
      columns: [
        {
          data: "SKU",
          render: function (data, type, row, meta) {
            return data != null
              ? '<a href="detail/' + row.listing_id + '">' + data + "</a>"
              : '<a  href="/edit_sku/" class="btn btn-warning">{{row.}}</a>';
          },
          orderable: false,
        },
        {
          data: "product_name",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : "Missing Title on Refurbed";
          },
        },
        {
          data: "stock_listed",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : 0;
          },
        },
        {
          data: "stock_available",
          orderable: false,
          render: function (data, type, row) {
            return data ? data : 0;
          },
        },
        {
          name: "quantityAdjust",
          orderable: false,
          render: function (data, type, row) {
            return quantityCounter(data, type, row, (marketplace = "RE"));
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
    reTable.on("init.dt", function () {
      htmx.process(document.body);
      let intervalId;
      $(document)
        .off("mousedown", ".plusRE")
        .on("mousedown", ".plusRE", function () {
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
      $(document)
        .off("mouseupRE", ".plusRE")
        .on("mouseupRE", ".plusRE", function () {
          clearInterval(intervalId);
        });
      $(document)
        .off("mousedown", ".minusRE")
        .on("mousedown", ".minusRE", function () {
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
      $(document)
        .off("mouseup", ".minusRE")
        .on("mouseup", ".minusRE", function () {
          clearInterval(intervalId);
        });
      $(document)
        .off("click", ".addRE")
        .on("click", ".addRE", function () {
          console.log("Add clicked RE");
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
            url: "/updateREquantity/",
            headers: { "X-CSRFToken": csrftoken },
            data: data,
            success: function (result) {
              getReData();
            },
          });
        });
    });
  }
};
