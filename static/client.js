// var i=0
//
// $("#addBlock").prop("disabled", false).click(function() {
//  i++
//  if (i%5 == 0) {
//   $(".slides").html($(".slides").html()+"<div style=\"background-color:green;\" id=\"slide-"+i+"\">lol</div>")
//  }
//  else
//   $(".slides").html($(".slides").html()+"<div id=\"slide-"+i+"\">"+i+"</div>")
// })

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
//        alert('No address generated.');
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

function generateAddresses(addressesToGenerate, apiURL, inputId, selectToUpdate, apiURLToFetch) {
    count = document.getElementById(inputId);
    if (+count.value < +count.min || +count.value > +count.max) {
        alert('Count of address input is not within bounds min='+count.min+', max='+count.max+'.');
        return;
    }
    fetch(`${apiURL}/?count=${count.value}`, {method: 'POST'})
//        .then(response => response.json())
//        .then(data => console.log(data));
        .then(alert(count.value+' new addresses were generated. You should see them in appropriate select element.'));
    fetchAddressesAndFillSelect(selectToUpdate, apiURLToFetch);
}

function createAToken() {
    var selectObj = document.getElementById('ownerAddressSelect');
    var timeout = document.getElementById('nftTimeout');
    const regex = /^\d+[.] /;
    selectedAddress = selectObj.options[selectObj.selectedIndex].text.replace(regex, '');

    if (selectObj.options.length === 0 || selectObj.selectedIndex === -1 || selectedAddress.substring(0, 2) != '0x') {
        alert('You have to generate owner addresses first and select one in the dropdown list.');
        return;
    }

    if (+timeout.value < +timeout.min || +timeout.value > +timeout.max) {
        alert('Timeout input is not within bounds min='+timeout.min+', max='+timeout.max+'.');
        return;
    }


//    if (selectedAddress.substring(0, 2) != '0x') {
//        alert('You have to generate owner addresses first and select one in the dropdown list.');
//        return;
//    }

    fetch(`/api/createToken/?timeout=${timeout.value}&ownerAddress=${selectedAddress}`, {method: 'POST'})
        .catch(error => {
            alert(error);
        })
        .then(response => response.json())
        .then(data => {
            if (data['success'] == true) {
                alert(data['message']);
            }
        });
    getAllTokens();
}

function getAllTokens() {
    fetch('/api/getAllTokens')
        .then(response => response.json())
        .then(data => {
            var table = document.getElementById("NFTTable");

            // Delete everything from table and set one row
            for (var i = table.rows.length-1; i >= 1; i--) {
              table.deleteRow(i);
            }

            if (data['nfts'].length === 0) {
              let row = table.insertRow();
              row.innerHTML = '<td colspan="5" style="text-align: center">Empty table so far</td>';
              return;
            } else {
              data['nfts'].forEach((item, i) => {
                let row = table.insertRow();
                for (var j = 0; j < table.rows[0].cells.length; j++) {
                  let tmpName = table.rows[0].cells[j].id.substring(3,);
                  let cellData = row.insertCell(j);
                  let tmpData = item[tmpName];
                  if (tmpData.length > 24) {
                    cellData.innerHTML = tmpData.substring(0,7) + ' . . . ' + tmpData.substring(tmpData.length-7, tmpData.length);
                  } else {
                    cellData.innerHTML = tmpData;
                  }
                }
              });
            }
        });
}

function engageNFT(addressSelectId, apiURL) {
  var selectObj = document.getElementById(addressSelectId);
  const regex = /^\d+[.] /;
  selectedAddress = selectObj.options[selectObj.selectedIndex].text.replace(regex, '');

  if (selectObj.options.length === 0 || selectObj.selectedIndex === -1 || selectedAddress.substring(0, 2) != '0x') {
      alert('You have to generate owner addresses first and select one in the dropdown list.');
      return;
  }
}

function changeNFTOwner() {

}

function assignUserToNFT() {
  const regex = /^\d+[.] /;
  var userSelectObj = document.getElementById('userAddressSelect');
  var ownerSelectObj = document.getElementById('ownerAddressSelect');
  var nftTokenIdInput = document.getElementById('nftTokenIdInput');
  var useOwnerAddInput = document.getElementById('nftUseOwnerAddress');

  selectedOwnerAddress = ownerSelectObj.options[ownerSelectObj.selectedIndex].text.replace(regex, '');
  if (useOwnerAddInput.checked) {
    selectedUserAddress = selectedOwnerAddress;
  } else {
    selectedUserAddress = userSelectObj.options[userSelectObj.selectedIndex].text.replace(regex, '');
  }

  if (ownerSelectObj.options.length === 0 || ownerSelectObj.selectedIndex === -1 || selectedOwnerAddress.substring(0, 2) != '0x' || selectedUserAddress.substring(0, 2) != '0x') {
      alert('You have to generate owner addresses first and select one in the dropdown list.');
      return;
  }

  fetch(`/api/setNFTUser?tokenId=${nftTokenIdInput.value}&newUserAddress=${selectedUserAddress}&ownerAddress=${selectedOwnerAddress}&ignoreUserCheck=${useOwnerAddInput.checked}`, {method: 'PUT'})
    .then(response => response.json())
    .then(data => {
      if (!data['success']) {
        alert(data['message']);
        return;
      } else {
        alert(data['message']);
        getAllTokens();
      }
    });
}

function setDifficulty() {
  var blockchainDifficulty = document.getElementById('blockchainDifficulty');
  if (+blockchainDifficulty.value < +blockchainDifficulty.min || +blockchainDifficulty.value > +blockchainDifficulty.max) {
      alert('Difficulty input is not within bounds min='+blockchainDifficulty.min+', max='+blockchainDifficulty.max+'.');
      return;
  }

  fetch(`/api/setBlockchainDifficulty?difficulty=${blockchainDifficulty.value}`, {method: 'PUT'})
    .then(response => response.json())
    .then(data => {
      alert(data['message']);
    });
}

function computeNewBlock() {
  prompt("Are you okay, man?");
}

function fetchBlockchain() {

}

fetchAddressesAndFillSelect('ownerAddressSelect', '/api/getOwnerAddresses');
fetchAddressesAndFillSelect('userAddressSelect', '/api/getUserAddresses');
getAllTokens();
fetchBlockchain();
