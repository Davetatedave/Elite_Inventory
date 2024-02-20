function showTooltip(element, message) {
  let tooltip = $(".tooltip-custom");

  if (!tooltip.length) {
    // Create tooltip if it doesn't exist
    tooltip = $('<div class="tooltip-custom"></div>').appendTo("body");
  }

  tooltip.html(message);
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

function checkAllProcessed() {
  var allProcessed = true;
  $("#deviceTable tbody tr").each(function () {
    if ($(this).find('td[data-processed="False"]').length > 0) {
      allProcessed = false;
      return false; // exit each loop early if any row is not processed
    }
  });
  $("#uploadButton").toggleClass("disabled");
}

function createsku(row_id) {
  const row = $("#" + row_id);
  const model = row.find(".model").html();
  const capacity = row.find(".capacity").html();
  const color = row.find(".color").html();
  const grade = row.find(".grade").html();
  const newSku = row.find("input.newsku").val();
  const csrftoken = Cookies.get("csrftoken");

  if (newSku == "") {
    showTooltip(row.find("input.newsku"), "Please Enter SKU");
    return;
  }
  $.ajax({
    url: "/new_sku/",
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    data: {
      model: model,
      capacity: capacity,
      color: color,
      grade: grade,
      newSku: newSku,
    },
    success: function (response) {
      console.log(response);
      row.attr("processed", "True");
      row.find(".skuInput").val(newSku).addClass("noneditable");
      row.find(".btn").remove();
      checkAllProcessed();
    },
    error: function (response) {
      showTooltip(row.find("input.newsku"), response.responseJSON.error);
    },
  });
}

function ignoreRow(row_id) {
  const row = $("#" + row_id);
  row.remove();
  checkAllProcessed();
}
