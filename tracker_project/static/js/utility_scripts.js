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
  // Tooltip for Missing IMEIs
  $("#buyShipping").on("click", function () {
    let imei = $("#imei").val();
    showTooltip($(this), "IMEIs Are Required");
  });
  // Get Shipping Price Button
  $("#getShippingPrice").on("click", function () {
    var shipper = $("#shipperSelect").val();
    console.log(shipper);
    if (shipper == "") {
      showTooltip($(this), "Please Select a Shipper");
    }
    if (shipper == "DHL") {
      $("#shippingPrice").val("£14");
    }
    if (shipper == "UPS") {
      $("#shippingPrice").val("£17");
    }
  });
});
