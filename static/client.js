var i=0

$("#addBlock").prop("disabled", false).click(function() {
 i++
 if (i%5 == 0) {
  $(".slides").html($(".slides").html()+"<div style=\"background-color:green;\" id=\"slide-"+i+"\">lol</div>")
 }
 else
  $(".slides").html($(".slides").html()+"<div id=\"slide-"+i+"\">"+i+"</div>")
})

function fetchAddressesAndFillSelect(selectId, apiURL) {
  var selectObj = document.getElementById(selectId);
  // Remove everything from ownerAddresses select
  for (let i = selectObj.options.length; i >= 0; i--) {
    selectObj.remove(i)
  }

  fetch(apiURL)
    .then(response => response.json())
    .then(data => {
      // console.log(data)
      if (data.length == 0) {
        let option = document.createElement("option");
        option.text = "No address generated";
        selectObj.add(option);
        selectObj.disabled = true;
      }
      else {
        data.forEach((item, i) => {
          var option = document.createElement("option");
          // Fill ownerAddresses select with values from API
          selectObj.disabled = false;
          option.text = i+1+'. '+item['wallet_address'];
          selectObj.add(option);
        });
      }
    }
  )
}

fetchAddressesAndFillSelect('ownerAddress', '/api/getOwnerAddresses')
fetchAddressesAndFillSelect('userAddress', '/api/getUserAddresses')
