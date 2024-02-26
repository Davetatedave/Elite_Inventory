$(document).ready(function () {
  filtersRefresh();
  $("#modelSelect, #capacitySelect, #colorSelect, #gradeSelect").val("");
});

function initialiseSelect2() {
  $("#modelSelect").select2({
    placeholder: "Select a Model",
    theme: "classic",
  });

  $("#capacitySelect").select2({
    placeholder: "Select a Capacity",
    theme: "classic",
  });

  $("#colorSelect").select2({
    placeholder: "Select a Color",
    theme: "classic",
  });

  $("#gradeSelect").select2({
    placeholder: "Select a Grade",
    theme: "classic",
  });
  $(".filter").on("change", function () {
    let data = {
      model: $("#modelSelect").val(),
      capacity: $("#capacitySelect").val(),
      color: $("#colorSelect").val(),
      grade: $("#gradeSelect").val(),
    };
    console.log(data);
    filtersRefresh();
  });
}

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
      $("#skuFilters").html(response);
      initialiseSelect2();
    },
    traditional: true,
  });
}
