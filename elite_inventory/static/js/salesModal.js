//Initialise Modal
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
