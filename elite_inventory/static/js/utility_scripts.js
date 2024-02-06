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
  // Toggle edit mode
  $(".edit-toggle").click(function () {
    console.log("Edit Toggle Clicked");
    $(".address-display").hide();
    $(".address-edit").show();
  });

  // Cancel edit mode
  $(".cancel-edit").click(function () {
    $(".address-edit").hide();
    $(".address-display").show();
  });

  // Handle form submission (example)
  $("#addressEditForm").submit(function (event) {
    event.preventDefault();
    // Here, you would collect the form data and send it to the server via AJAX or a similar method
    const formData = {
      name: $("#name").val(),
      street: $("#street").val(),
      city: $("#city").val(),
      state: $("#state").val(),
      postalCode: $("#postalCode").val(),
    };
    console.log(formData); // For demonstration; replace with AJAX call

    // Optionally, update the display values and switch back to display mode
    $("address").html(
      `<strong>${formData.name}</strong><br>${formData.street}<br>${formData.city}, ${formData.state} ${formData.postalCode}<br>`
    );
    $(".address-edit").hide();
    $(".address-display").show();
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
          accountNumber: "425992913",
          originCountryCode: "GB",
          originPostalCode: "BT2 7BG",
          originCityName: "Belfast",
          destinationCountryCode: "GB",
          destinationPostalCode: "BT2 7BG",
          destinationCityName: "Belfast",
          weight: "0.5",
          length: "15",
          width: "10",
          height: "5",
          plannedShippingDate: new Date().toISOString().split("T")[0],
          isCustomsDeclarable: "false",
          unitOfMeasurement: "metric",
        },
        success: function (response) {
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
    if ($("#shippingPrice").val() == "") {
      showTooltip($(this), "Please Select Shipping Method");
    } else {
      $.ajax({
        url: "/shipping_label/",
        method: "GET",
        data: {
          shipping_service: $("#shippingPrice").val(),
          customer: $("#buyShipping").data("customer"),
          imeis: imeis,
        },
        success: function (response) {
          $("#label").replaceWith(response);
        },
      });
    }
  });
});
