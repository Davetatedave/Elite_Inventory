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

// After Modal Load
document.addEventListener("htmx:afterRequest", function (evt) {
  if (evt.detail.target.id === "modals-here") {
    initialiseModal();
  }
});

// Modal
function reloadModal() {
  var so_id = $("#order").data("so");
  $.ajax({
    url: "./detail/" + so_id,
    success: function (response) {
      $("#modals-here").html(response);
      initialiseModal();
    },
  });
}
function initialiseModal() {
  var so_id = $("#order").data("so");
  // Commit IMEI
  $(".imeis input[type='number']").on("input", function () {
    var value = $(this).val();
    var commitButton = $(this).siblings(".commitIMEI"); // Select the commit button
    if (value.length > 15) {
      // If input is longer than 15 chars, truncate it
      $(this).val(value.substring(0, 15));
      showTooltip($(this), "IMEI Must Be 15 Characters");
    }
    if (value.length >= 15) {
      console.log("IMEI is 15");
      // If input is longer than 15 chars, swap classes and enable the button
      commitButton.removeClass("btn-secondary").addClass("btn-success");
      commitButton.removeAttr("disabled");
      commitButton.off("click").on("click", function () {
        var imei = $(this).siblings("input").val();
        var requestedSKU = $(".infobox .requestedSKU strong").text();
        var csrftoken = Cookies.get("csrftoken");
        var forceCommit = $(this).closest("div").find(".force");
        var forceCommitval = forceCommit.prop("checked");
        var itemId = $(this).closest(".infobox").data("item-id");

        if (forceCommit == true) {
          if (!confirm("Are you sure you want to force commit this IMEI?")) {
            return;
          }
        }
        $.ajax({
          url: "/commit_imei/",
          method: "POST",
          headers: { "X-CSRFToken": csrftoken },
          data: {
            imei: imei,
            so_id: so_id,
            item_id: itemId,
            force_commit: forceCommitval,
            sku: requestedSKU,
          },
          success: function (response) {
            console.log(response);
            reloadModal();
          },
          error: function (response) {
            showTooltip(
              $(".imeis input[type='number']"),
              response.responseJSON.message
            );
          },
        });
      });
    } else {
      console.log("IMEI is not 15 (it's" + value.length + ")");
      // Otherwise, reset to the original state
      commitButton.addClass("btn-secondary").removeClass("btn-success");
      commitButton.attr("disabled", "disabled");
    }
  });

  //Remove IMEI
  $(".commitedImei .removeIMEI").click(function () {
    var device = $(this).data("device");
    if (!confirm("Are you sure you want to remove this IMEI from the order?")) {
      return;
    }
    $.ajax({
      url: "/remove_imei/",
      method: "POST",
      headers: { "X-CSRFToken": Cookies.get("csrftoken") },
      data: { device: device },
      success: reloadModal(),
    });
  });

  /// Load Shipping Info
  country = $("#countryInit").val();
  $("#country option[value=" + country + "]").prop("selected", true);
  console.log("Country " + country);
  $.ajax({
    method: "GET",
    url: "/shipment_details/" + so_id,
    success: function (response) {
      $("#shipping-info").replaceWith(response);
    },
  });
  // Toggle address edit mode
  let edited = [];
  $(".edit-toggle").click(function () {
    console.log("Edit Toggle Clicked");
    $("#addressEditForm").removeClass("noneditable");
    const inputs = document.querySelectorAll(
      '#addressEditForm input[type="text"],select'
    );
    inputs.forEach((input) => {
      input.addEventListener("change", function () {
        // Flag this input as edited by adding it to the `edited` array if not already included.
        if (!edited.includes(this.id)) {
          edited.push(this.id);
          console.log(this.id + " edited");
        }
      });
    });
  });

  // Cancel edit mode
  $(".cancel-edit").click(function () {
    $("#addressEditForm").addClass("noneditable");
  });

  // Handle form submission
  $("#addressEditForm").submit(function (event) {
    event.preventDefault();
    let formData = {
      customer_id: $("#name").data("customer-id"), // Assuming this is correct and consistent with your form structure
    };

    // Only include edited fields in formData
    edited.forEach((fieldId) => {
      formData[fieldId] = $("#" + fieldId).val();
    });
    $.ajax({
      url: "/update_address/",
      method: "POST",
      headers: { "X-CSRFToken": Cookies.get("csrftoken") },
      data: formData,

      success: function (response) {
        // Optionally, update the display values and switch back to display mode
        $("address").html(
          `<strong>${response.name}</strong><br>${response.street}<br>${response.city}, ${response.state} ${response.postalCode}<br>`
        );
        $("#addressEditForm").addClass("noneditable");
      },
    });
  });

  // Get Shipping Price Button
  $("#getShippingPrice").on("click", function () {
    var shipper = $("#shipperSelect").val();
    console.log(shipper);
    if (shipper == "") {
      showTooltip($(this), "Please Select a Shipper");
    }
    if (shipper == "DHL") {
      let csrftoken = Cookies.get("csrftoken");
      $.ajax({
        beforeSend: function () {
          $("#overlay").fadeIn(50);
        },
        url: "/shipping_rates/",
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        dataType: "html",
        data: {
          customer: $("#getShippingPrice").data("customer"),
        },
        error: function (xhr, textStatus, errorThrown) {
          console.log("Error");
          const error = JSON.parse(xhr.responseText).error;
          console.log(error);
          $("#overlay").fadeOut(50);
          showTooltip($("#editAddress"), error);
        },
        success: function (response) {
          $(".estDelivery").remove();
          $("#shippingPrice").replaceWith(response);
          $("#overlay").fadeOut(50);
        },
      });
    }
    if (shipper == "UPS") {
      $("#shippingPrice").val("£17");
    }
  });

  // Buy Shipping Button
  $("#buyShipping").on("click", function () {
    let imeis = [];
    $(".imeis").each(function () {
      let imei = $(this).val();
      if (imei) imeis.push(imei);
      else imeis.push("Missing"); // Add the value to the array if it's not empty
    });
    if (!imeis.includes("Missing") && $("#serviceSelect").val() !== "") {
      $.ajax({
        beforeSend: function () {
          $("#overlay").fadeIn(50);
        },
        url: "/shipping_label/",
        method: "GET",
        data: {
          shipping_service: $("#serviceSelect").val(),
          customer: $("#buyShipping").data("customer"),
          salesOrder: $("#order").data("so"),
          imeis: imeis,
        },
        success: function (response) {
          $.ajax({
            method: "GET",
            url: "/shipment_details/" + so_id,
            success: function (response) {
              $("#shipping-info").replaceWith(response);
              $("#overlay").fadeOut(50);
              window.open("get_label/" + so_id, "_blank");
            },
          });
        },
      });
    } else {
      if (imeis.includes("Missing")) {
        showTooltip($(this), "All IMEIs Are Required");
      }
      if ($("#serviceSelect").val() == "") {
        console.log($("#serviceSelect").val());
        showTooltip($(this), "Please Select Shipping Method");
      }
    }
  });
}
