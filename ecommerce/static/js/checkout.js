$(document).ready(function(){
    "use strict"
    let arrData = [];
    let wilaya_arr = [];
    let wilaya_select=document.getElementsByClassName("wilaya");
    let commun_select=document.getElementById("commun");
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
          let shipping = document.getElementById('shipping');
          let total_1 = document.getElementById('total_1');

          // and display deliveryfees
          $.ajax({
            url: "/api/getcommunstrus/",
            type: 'GET',
            dataType: 'json', // added data type
            success: function(data) {
              data['deliveryfees'].forEach(element=>{
              if(element.wilaya_name==current_wilaya){
                shipping.innerHTML=`دج ${element.desk_fee}`;
                total_1.innerHTML=`دج ${total_order+element.desk_fee}`;


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
        let total_2 = document.getElementById('total_2');
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

  }) // end document ready

  let form = document.getElementById("form");
  let form2 = document.getElementById("form2");

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
    let userFormData = {
      name: form.name.value,
      phone: form.phone.value,
      email: form.email.value,
      total: total,
    };
    let shippingInfo = {
      address: "",
      city: form.commun.value,
      state: form.wilaya.value,
      
    };
    console.log("Shipping Info:", shippingInfo);
    console.log("User Info:", userFormData);

/*    let url = "/process_order/";
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({ form: userFormData , shipping: shippingInfo,stop_disk:true  }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Success:", data);
        cart = {};
        document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
        window.location.href = "/checkout/success/";
      })
      .catch((error) => {
        console.error("Error:", error);
      }); */
      $.ajax({
        type: "POST",
        beforeSend: function (request) {
          request.setRequestHeader("Content-Type", "application/json");
          request.setRequestHeader("X-CSRFToken", csrftoken);
        },
        url: "/api/process_order/",
        data: JSON.stringify({ form: userFormData , shipping: shippingInfo,stop_disk:true  }),
        processData: true,
        success: function (msg) {
          console.log("success ajax" + msg);
          cart = {};
          document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
          window.location.href = "/checkout/success/";
        },
      });
  }
  function submitFormData2() {
    console.log("submite button clicked");
    let userFormData2 = {
      name: form2.name.value,
      phone: form2.phone.value,
      email: form2.email.value,
      total: total,
    };
    let shippingInfo2 = {
      address: form2.address.value,
      city: form2.commun.value,
      state: form2.wilaya.value,
    };
/*     let url = "/process_order/";
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
        window.location.href = "/checkout/success/";
      })
      .catch((error) => {
        console.error("Error:", error);
      }); */
      $.ajax({
        type: "POST",
        beforeSend: function (request) {
          request.setRequestHeader("Content-Type", "application/json");
          request.setRequestHeader("X-CSRFToken", csrftoken);
        },
        url: "/api/process_order/",
        data: JSON.stringify({ form: userFormData2, shipping: shippingInfo2,stop_disk:false }),
        processData: true,
        success: function (msg) {
          console.log("success ajax" + msg);
          cart = {};
          document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
          window.location.href = "/checkout/success/";
        },
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