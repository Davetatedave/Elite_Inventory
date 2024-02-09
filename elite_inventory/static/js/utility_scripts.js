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
    zIndex: 4999,
  });

  tooltip.stop().fadeIn(150);

  // Hide tooltip after some time (optional)
  setTimeout(function () {
    tooltip.fadeOut();
  }, 3000);
}

$("#shipperSelect").select2({
  placeholder: "Select a Shipper",
  theme: "classic",
});

document.addEventListener("htmx:afterRequest", function (evt) {
  if (evt.detail.target.id === "modals-here") {
    console.log("Modal Loaded");
    /// Load Shipping Info
    let so_id = $("#order").data("so");
    $.ajax({
      method: "GET",
      url: "/shipment_details/" + so_id,
      success: function (response) {
        $("#shipping-info").replaceWith(response);
      },
    });
    // Toggle edit mode
    let edited = [];
    $(".edit-toggle").click(function () {
      console.log("Edit Toggle Clicked");
      $(".address-display").hide();
      $(".address-edit").show();
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
      $(".address-edit").hide();
      $(".address-display").show();
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
          $(".address-edit").hide();
          $(".address-display").show();
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
            console.log(xhr);
            const error = xhr.responseText;
            $("#overlay").fadeOut(50);
            showTooltip($(".address-display"), error);
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

    // Tooltip for Missing IMEIs
    $("#buyShipping").on("click", function () {
      let imeis = [];
      $(".imeis").each(function () {
        let imei = $(this).val();
        if (imei) imeis.push(imei);
        else imeis.push("Missing"); // Add the value to the array if it's not empty
      });
      if (imeis.includes("Missing")) {
        showTooltip($(this), "All IMEIs Are Required");
      }
      if ($("#serviceSelect").val() == "") {
        console.log($("#serviceSelect").val());
        showTooltip($(this), "Please Select Shipping Method");
      } else {
        $.ajax({
          url: "/shipping_label/",
          method: "GET",
          data: {
            shipping_service: $("#serviceSelect").val(),
            customer: $("#buyShipping").data("customer"),
            salesOrder: $("#order").data("so"),
            imeis: imeis,
          },
          success: function (response) {
            $("#label").replaceWith(response);
          },
        });
      }
    });
  }
});
