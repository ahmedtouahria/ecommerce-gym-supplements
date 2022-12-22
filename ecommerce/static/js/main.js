//ADD THIS PIECE OF CODE IN YOUR JS OR HTML PAGE UNDER SCRIPT
"use strict";
$(document).ready(function () {
//search .autocomplete
let search_nav = $("#search_nav"); // for keyup event
let result_nav = $("#result_product ul"); // for append result 
let result_product = $("#result_product"); // for shadow style 
/* KEYUP EVENT */
search_nav.keyup(function (e) {
  result_nav.html("");
  let data = $(this).val();
  if ($.trim(data).length > 0) {
    $.ajax({
      url: "/api/products/",
      type: "GET",
      data: {
        search: data,
      },
      success: function (res) {
        // ADD boxshadow style
        result_product.addClass('shadow-sm p-3 mb-5 bg-white rounded').removeClass('d-none');
        if(res.length>0){
        $.each(res, function (key, value) { result_nav.append(
            `<li class="d-flex my-2 "><img src="${value.image}" height="30" width="30"><a style="color: black;font-weight: 500; " class="mx-2"href="/products/${value.slug}">${value.name}</a></li>`
          );
        });}
        else
        result_nav.append(
            `<li class="d-flex my-2"><a style="color: black;font-weight: 500;" class="mx-2">Aucun résultat</a></li>`
          );
      },
    });
  }
  // REMOVE boxshadow style
  else
  result_product.removeClass('shadow-sm p-3 mb-5 bg-white rounded').addClass('d-none');

});
const tabs = document.querySelectorAll("[data-target]"),
tabContents = document.querySelectorAll("[data-content]");
tabs.forEach((tab) => {
tab.addEventListener("click", () => {
const target = document.querySelector(tab.dataset.target);
tabContents.forEach((tc) => {
      tc.classList.remove("is-active");
    });
target.classList.add("is-active");

tabs.forEach((t) => {
      t.classList.remove("is-active");
    });
    tab.classList.add("is-active");
  });
});
$(".custom-select").niceSelect("destroy");
//--------- script to hundel sidebar for mini devices---------//
$("#sidebarCollapse").on("click", function () {
  $("#sidebar").addClass("active");
});
$("#sidebarCollapseX").on("click", function () {
  $("#sidebar").removeClass("active");
});
$("#sidebarCollapse").on("click", function () {
  if ($("#sidebar").hasClass("active")) {
    $(".overlay").addClass("visible");
    // console.log("it's working!");
  }
});
$("#sidebarCollapseX").on("click", function () {
  $(".overlay").removeClass("visible");
});
setTimeout(() => {
  if ($("#alert").length > 0) {
    $("#alert").fadeOut();
  }
}, 4000);
  const loading = $("#loading");
  const body = $("#body");
    loading.addClass("d-none");
    body.removeClass("d-none");
    $("select").niceSelect();
    $(".s_Product_carousel").owlCarousel({
      items: 1,
      autoplay: true,
      autoplayTimeout: 5000,
      loop: true,
      nav: false,
      dots: true,
    });
////////////////////////////////////////////////////////////

});
//display cart item 
function getCartItem() {
  $.ajax({
    url: "/api/cartitemApi/",
    type: "GET",
    success: function (res) {
      console.log(res.cartItem);
      $(".cartItem").html(res.cartItem);
    },
  });
}
// mobile menu variables
const mobileMenuOpenBtn = document.querySelectorAll(
"[data-mobile-menu-open-btn]"
);
const mobileMenu = document.querySelectorAll("[data-mobile-menu]");
const mobileMenuCloseBtn = document.querySelectorAll("[data-mobile-menu-close-btn]");
const overlay = document.querySelector("[data-overlay]");
for (let i = 0; i < mobileMenuOpenBtn.length; i++) {
// mobile menu function
const mobileMenuCloseFunc = function () {
  mobileMenu[i].classList.remove("active");
  overlay.classList.remove("active");
};
mobileMenuOpenBtn[i].addEventListener("click", function () {
mobileMenu[i].classList.add("active");
  overlay.classList.add("active");
});
mobileMenuCloseBtn[i].addEventListener("click", mobileMenuCloseFunc);
overlay.addEventListener("click", mobileMenuCloseFunc);
}
// accordion variables
const accordionBtn = document.querySelectorAll("[data-accordion-btn]");
const accordion = document.querySelectorAll("[data-accordion]");
for (let i = 0; i < accordionBtn.length; i++) {
accordionBtn[i].addEventListener("click", function () {
  const clickedBtn =
    this.nextElementSibling.classList.contains("active");
  for (let i = 0; i < accordion.length; i++) {
    if (clickedBtn) break;
    if (accordion[i].classList.contains("active")) {
      accordion[i].classList.remove("active");
      accordionBtn[i].classList.remove("active");
    }
  }
  this.nextElementSibling.classList.toggle("active");
  this.classList.toggle("active");
});
}
var arrData = [];
var wilaya_arr = [];
var wilaya_select=document.getElementsByClassName("wilaya");
var commun_select=document.getElementById("commun");
var commun_select2=document.getElementById("commun2");
// load yalidin wilaya from url 
$.ajax({
        url: "/getwilaya",
        type: 'GET',
        dataType: 'json', // added data type
        success: function(data) {
          data.forEach(element=>{
          wilaya_select[0].innerHTML+=`<option name="state" value="${element.name}">${element.id} ${element.name}</option>`;
          })
        }
      });
wilaya_select[0].onchange=function(e){
        console.log(e.target.value);
        commun_select.innerHTML='';
        let current_wilaya=e.target.value;
        //display related communs 
        $.ajax({
        url: "/api/getcommunstrus/",
        type: 'GET',
        dataType: 'json', // added data type
        success: function(data) {
          data['communs'].forEach(element=>{
          if(element.wilaya_name==current_wilaya){
            commun_select.innerHTML+=
            `<option name="commun" value="${element.name}">${element.name}</option>`;}
          })

        },
      });
      var shipping = document.getElementById('shipping');
      var total_1 = document.getElementById('total_1');

      // and display deliveryfees
      $.ajax({
        url: "/api/getcommunstrus/",
        type: 'GET',
        dataType: 'json', // added data type
        success: function(data) {
          data['deliveryfees'].forEach(element=>{
          if(element.wilaya_name==current_wilaya){
            shipping.innerHTML=`${element.desk_fee} DA`;
            total_1.innerHTML=`${total_order+element.desk_fee} DA`;


          }
          })

        },
      });
    };
    $.getJSON("/static/json/communs.json", function (data) {
      $.each(data["data"], function (index, value) {
        wilaya_arr.push(value.wilaya_name);
        arrData = data["data"];
      });

      // Remove duplicates. We want unique wilaya.
      wilaya_arr = Array.from(new Set(wilaya_arr));

      $.each(wilaya_arr, function (index, value) {
        $("#wilaya2").append(
          '<option name="wilaya" value="' + value + '">' + value + "</option>"
        );
      });
    });
    var total_2 = document.getElementById('total_2');
    $("#wilaya2").change(function () {
      let wilayaTarget = this.options[this.selectedIndex].value;
      $("shipping_home").html()
      let filterData = arrData.filter(function (value) {
        return value.wilaya_name == wilayaTarget;
      });
      $("#commun2")
        .empty()  
      $.each(filterData, function (index, value) {
        $("#commun2").append(
          '<option name="commun" value="' +
            value.name +
            '">' +
            value.name +
            "</option>"
        );
      });
                // and display deliveryfees
    $.ajax({
      url: "/api/getcommunstrus/",
      type: 'GET',
      dataType: 'json', // added data type
      success: function(data) {
        data['deliveryfees'].forEach(element=>{
        if(element.wilaya_name==wilayaTarget){
          shipping_home.innerHTML=`${element.home_fee} DA`;
          total_2.innerHTML=`${total_order+element.home_fee} DA`;

        }
        })

      },
    });
    });


var form = document.getElementById("form");
var form2 = document.getElementById("form2");

form.addEventListener("submit", function (e) {
e.preventDefault();
submitFormData();
});
form2.addEventListener("submit", function (e) {
e.preventDefault();
submitFormData2();
});

function submitFormData() {
console.log("submite button clicked");
var userFormData = {
  name: form.name.value,
  phone: form.phone.value,
  total: total,
};
var shippingInfo = {
  address: form.address.value,
  city: form.commun.value,
  state: form.wilaya.value,
  zipcode: form.zipcode.value,
  
};
console.log("Shipping Info:", shippingInfo);
console.log("User Info:", userFormData);

var url = "/process_order/";
fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "applicaiton/json",
    "X-CSRFToken": csrftoken,
  },
  body: JSON.stringify({ form: userFormData , shipping: shippingInfo,stop_disk:true  }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Success:", data);
    cart = {};
    document.cookie =
      "cart=" + JSON.stringify(cart) + ";domain=;path=/";
    window.location.href = "{% url 'products' %}";
  })
  .catch((error) => {
    console.error("Error:", error);
  });
}
function submitFormData2() {
console.log("submite button clicked");
var userFormData2 = {
  name: form2.name.value,
  phone: form2.phone.value,
  total: total,
};
var shippingInfo2 = {
  address: form2.address.value,
  city: form2.commun.value,
  state: form2.wilaya.value,
  zipcode: form2.zipcode.value,
};
var url = "/process_order/";
fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrftoken,
  },
  body: JSON.stringify({ form: userFormData2, shipping: shippingInfo2,stop_disk:false }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Success:", data);
    cart = {};
    document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
    window.location.href = "{% url 'products' %}";
  })
  .catch((error) => {
    console.error("Error:", error);
  });
}
const tabs = document.querySelectorAll("[data-target]"),
tabContents = document.querySelectorAll("[data-content]");
tabs.forEach((tab) => {
tab.addEventListener("click", () => {
const target = document.querySelector(tab.dataset.target);
tabContents.forEach((tc) => {
  tc.classList.remove("is-active");
});
target.classList.add("is-active");

tabs.forEach((t) => {
  t.classList.remove("is-active");
});
tab.classList.add("is-active");
});
});