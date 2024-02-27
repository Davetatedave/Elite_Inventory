$(document).ready(function () {
  filtersRefresh();
  $("#modelSelect, #capacitySelect, #colorSelect, #gradeSelect").val("");
});

// $("#modelSelect").select2({
//   placeholder: "Select a Model",
//   theme: "classic",
// });

// $("#capacitySelect").select2({
//   placeholder: "Select a Capacity",
//   theme: "classic",
// });

// $("#colorSelect").select2({
//   placeholder: "Select a Color",
//   theme: "classic",
// });

// $("#gradeSelect").select2({
//   placeholder: "Select a Grade",
//   theme: "classic",
// });

$(".filter").on("change", function () {
  let data = {
    model: $("#modelSelect").val(),
    capacity: $("#capacitySelect").val(),
    color: $("#colorSelect").val(),
    grade: $("#gradeSelect").val(),
  };
  filtersRefresh();
});

function filtersRefresh() {
  $.ajax({
    url: "/edit_skuajax/",
    type: "POST",
    headers: { "X-CSRFToken": Cookies.get("csrftoken") },
    data: {
      model: $("#modelSelect").val(),
      capacity: $("#capacitySelect").val(),
      color: $("#colorSelect").val(),
      grade: $("#gradeSelect").val(),
    },
    success: function (response) {
      // Set the selected value
      $("#modelSelect").val(response.selected_model);

      // Hide existing options for color
      $("#colorSelect option").hide();

      // // Show options from the response
      $.each(response.color, function (index, value) {
        $("#colorSelect option[value='" + value + "']").show();
      });

      // Set the selected value
      $("#colorSelect").val(response.selected_color);

      // Hide existing options for capacity
      $("#capacitySelect option").hide();

      // Show options from the response
      $.each(response.capacity, function (index, value) {
        $("#capacitySelect option[value='" + value + "']").show();
      });

      // Set the selected value
      $("#capacitySelect").val(response.selected_capacity);

      // Hide existing options for grade
      $("#gradeSelect option").hide();

      // Show options from the response
      $.each(response.grade, function (index, value) {
        $("#gradeSelect option[value='" + value + "']").show();
      });

      // Set the selected value
      $("#gradeSelect").val(response.selected_grade);

      if (response.internal_skus) {
        $("#internalSku").val(response.internal_skus);
        $("#internalSku").data("id", response.sku_id);
      }
      if (response.bm_skus) {
        $("#BMSku").val(response.bm_skus);
        $("#BMSku").data("id", response.bm_id);
      }
    },
    traditional: true,
  });
}

$(".skus").on("change", function () {
  this.value = this.value.toUpperCase();
  updateButton = $(this).closest(".input-group").find(".btn");
  updateButton.removeClass("btn-outline-secondary").addClass("btn-success");
  updateButton.on("click", function () {
    if (confirm("Are you sure you want to update the SKU?")) {
      let new_sku = $(this).closest(".input-group").find(".skus").val();
      let id = $(this).closest(".input-group").find("input").data("id");
      let skuType = updateButton.data("sku_type");
      let data = {
        new_sku: new_sku,
        id: id,
        skuType: skuType,
      };
      $.ajax({
        url: "/updateSKU/",
        type: "POST",
        headers: { "X-CSRFToken": Cookies.get("csrftoken") },
        data: data,
        success: function (response) {
          updateButton
            .removeClass("btn-success")
            .addClass("btn-outline-secondary");
        },
      });
    }
  });
});
