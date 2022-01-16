var nftHidden = false;
var blockchainHidden = true;

$('#showTable').click(function() {
  if (blockchainHidden && !nftHidden) {
    $('#NFTTable').hide();
    $('#blocksTable').show();
    nftHidden = true;
    blockchainHidden = false;
    $('#showTable').html('Hide table with blocks');
  }
  else {
    $('#NFTTable').show();
    $('#blocksTable').hide();
    nftHidden = false;
    blockchainHidden = true;
    $('#showTable').html('Hide table with nfts');
  }
})

function addBlockUITable(block, table) {
  var isPresent = false;
  let row = table.insertRow();
  for (var j = 0; j < table.rows[0].cells.length; j++) {
    let tmpName = table.rows[0].cells[j].id.substring(3,);
    let cellData = row.insertCell(j);
    let tmpData;
    switch (tmpName) {
      case 'no_transactions':
          tmpData = block['transactions'].length;
        break;
      case 'nft_present':
        if (block['transactions'].length > 0) {
          block['transactions'].forEach((transaction, j) => {
              isPresent = !isPresent && transaction['contractData'] != null ? true : false;
          });
        }
        tmpData = isPresent ? 'yes' : 'no';
        break;
      default:
        tmpData = block[tmpName];
    }
    // if (tmpData.length > 24) {
    //   cellData.innerHTML = tmpData.substring(0,7) + ' . . . ' + tmpData.substring(tmpData.length-7, tmpData.length);
    // } else {
      cellData.innerHTML = tmpData;
    // }
  }

  return isPresent;
}

function addBlockUISlides(block, nftPresent) {
  if (nftPresent) {
   $(".slides").html($(".slides").html()+`<div style="background-color:green;" id="slide-${block['index']}">${block['index']}</div>`)
  }
  else
   $(".slides").html($(".slides").html()+`<div id="slide-${block['index']}">${block['index']}</div>`)
}

function addNFTUITable(nft, table) {
  let row = table.insertRow();
  for (var j = 0; j < table.rows[0].cells.length; j++) {
    let tmpName = table.rows[0].cells[j].id.substring(3,);
    let cellData = row.insertCell(j);
    let tmpData = nft[tmpName];
    if (tmpData != null && tmpData.length > 24) {
      cellData.innerHTML = tmpData.substring(0,7) + ' . . . ' + tmpData.substring(tmpData.length-7, tmpData.length);
    } else if (tmpData == null) {
      cellData.innerHTML = 'No user';
    } else {
      cellData.innerHTML = tmpData;
    }
  }
}

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
          selectObj.options[0].selected = true;
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
    fetch(`${apiURL}?count=${count.value}`, {method: 'POST'})
//        .then(response => response.json())
//        .then(data => console.log(data));
        .then(alert(count.value+' new addresses were generated. You should see them in appropriate select element.'));
    fetchAddressesAndFillSelect(selectToUpdate, apiURLToFetch);
}

function createAToken() {
    var selectObj = document.getElementById('ownerAddressSelect');
    var timeout = document.getElementById('nftTimeout');
    const regex = /^\d+[.] /;
    let selectedAddress = selectObj.options[selectObj.selectedIndex].text.replace(regex, '');

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

    fetch(`/api/createToken?timeout=${timeout.value}&ownerAddress=${selectedAddress}`, {method: 'POST'})
        .catch(error => {
            alert(error);
        })
        .then(response => response.json())
        .then(data => {
            if (data['success'] == true) {
                alert(data['message']);
                console.log(data['transaction']);
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
              row.innerHTML = `<td colspan="${table.rows[0].cells.length}" style="text-align: center">Empty table so far</td>`;
              return;
            } else {
              data['nfts'].forEach((nft, i) => {
                addNFTUITable(nft, table);
              });
            }
        });
}

function engageNFT(addressSelectId, apiURL) {
  var selectObj = document.getElementById(addressSelectId);
  var nftTokenIdInput = document.getElementById('nftTokenIdInput');
  var useOwnerAddInput = document.getElementById('nftUseOwnerAddress');
  const regex = /^\d+[.] /;

  let userOrOwner = addressSelectId === "ownerAddressSelect" ? "ownerAddressEngage" : "userAddressEngage";

  let selectedAddress = useOwnerAddInput.checked ? document.getElementById('ownerAddressSelect').options[document.getElementById('ownerAddressSelect').selectedIndex].text.replace(regex, '') : selectObj.options[selectObj.selectedIndex].text.replace(regex, '');

  if (selectObj.options.length === 0 || selectObj.selectedIndex === -1 || selectedAddress.substring(0, 2) != '0x') {
      alert('You have to generate owner addresses first and select one in the dropdown list.');
      return;
  }

  fetch(`${apiURL}?tokenId=${nftTokenIdInput.value}&${userOrOwner}=${selectedAddress}&ignoreUserCheck=${useOwnerAddInput.checked}`, {method: 'PUT'})
    .then(response => response.json())
    .then(data => {
      alert(data['message']);
      console.log(data['transaction']);
      getAllTokens();
    });
}

// TODO: Do this, man!
function changeNFTOwner() {
  const regex = /^(\d+)[.] /;
  var ownerSelectObj = document.getElementById('ownerAddressSelect');
  var nftTokenIdInput = document.getElementById('nftTokenIdInput');
  var useOwnerAddInput = document.getElementById('nftUseOwnerAddress');

  let selectedOwnerAddress = [];
  if ($('#ownerAddressSelect').val().length != 2 || $('#ownerAddressSelect').val()[0] === $('#ownerAddressSelect').val()[1]) {
    alert('You have to choose two different owners.');
    return;
  } else {
    // let selectedIndexes = [];
    $('#ownerAddressSelect').val().forEach((address, i) => {
      // selectedIndexes.push(address.match(regex)[1]);
      selectedOwnerAddress.push(address.replace(regex, ''));
    });
  }

  console.log(selectedOwnerAddress);

  if (ownerSelectObj.options.length === 0 || ownerSelectObj.selectedIndex === -1 || selectedOwnerAddress[0].substring(0, 2) != '0x' || selectedOwnerAddress[1].substring(0, 2) != '0x') {
      alert('You have to generate owner addresses first and select one in the dropdown list.');
      return;
  }

  fetch(`/api/transferNFTOwner?tokenId=${nftTokenIdInput.value}&newOwnerAddress=${selectedOwnerAddress[1]}&ownerAddress=${selectedOwnerAddress[0]}`, {method: 'PUT'})
    .then(response => response.json())
    .then(data => {
      if (!data['success']) {
        alert(data['message']);
        return;
      } else {
        alert(data['message']);
        getAllTokens();
        console.log(data['transaction']);
      }
    });
}

function assignUserToNFT() {
  const regex = /^\d+[.] /;
  var userSelectObj = document.getElementById('userAddressSelect');
  var ownerSelectObj = document.getElementById('ownerAddressSelect');
  var nftTokenIdInput = document.getElementById('nftTokenIdInput');
  var useOwnerAddInput = document.getElementById('nftUseOwnerAddress');

  let selectedOwnerAddress = ownerSelectObj.options[ownerSelectObj.selectedIndex].text.replace(regex, '');
  if (useOwnerAddInput.checked) {
    if ($('#ownerAddressSelect').val().length > 1) {
      alert('You have to choose one owner only.');
      return;
    }
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
        console.log(data['transaction']);
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
  fetch(`/api/computeNewBlock`, {method: 'PUT'})
    .then(response => response.json())
    .then(data => {
      alert(data['message']);
      var table = document.getElementById("blocksTable");

      // Delete everything from table and set one row
      for (var i = table.rows.length-1; i >= 1; i--) {
        table.deleteRow(i);
      }
      isNFTPresent = addBlockUITable(data['computedBlock'], table);
      // $(".slides").html("");
      addBlockUISlides(data['computedBlock'], isNFTPresent);
      console.log(data['computedBlock']['transactions']);
    });
}

function fetchBlockchain() {
  fetch('/api/getBlockchain')
    .then(response => response.json())
    .then(data => {
      var table = document.getElementById("blocksTable");

      // Delete everything from table and set one row
      for (var i = table.rows.length-1; i >= 1; i--) {
        table.deleteRow(i);
      }

      $(".slides").html("");

      if (data['blocks'].length === 0) {
        let row = table.insertRow();
        row.innerHTML = `<td colspan="${table.rows[0].cells.length}" style="text-align: center">Empty table so far</td>`;
        return;
      } else {
        data['blocks'].forEach((block, i) => {
          isNFTPresent = addBlockUITable(block, table);
          addBlockUISlides(block, isNFTPresent);
        });
      }
    });
}

function postTransaction() {
  const regex = /^\d+[.] /;
  var userSelectObj = document.getElementById('userAddressSelect');
  var ownerSelectObj = document.getElementById('ownerAddressSelect');
  var amountInput = document.getElementById('trxAmountInput');

  selectedOwnerAddress = ownerSelectObj.options[ownerSelectObj.selectedIndex].text.replace(regex, '');
  selectedUserAddress = userSelectObj.options[userSelectObj.selectedIndex].text.replace(regex, '');

  if (ownerSelectObj.options.length === 0 || ownerSelectObj.selectedIndex === -1 || selectedOwnerAddress.substring(0, 2) != '0x' || selectedUserAddress.substring(0, 2) != '0x') {
      alert('You have to generate addresses first and select one in the dropdown list.');
      return;
  }

  if (+amountInput.value < +amountInput.min) {
      alert('Transaction amount input is not within bounds min='+amountInput.min);
      return;
  }

  fetch(`/api/postTransaction?sender=${selectedOwnerAddress}&recipient=${selectedUserAddress}&amount=${amountInput.value}`, {method: 'POST'})
    .then(response => response.json())
    .then(data => {
      alert(data['message']);
      console.log(data['transaction']);
    });
}

fetchAddressesAndFillSelect('ownerAddressSelect', '/api/getOwnerAddresses');
fetchAddressesAndFillSelect('userAddressSelect', '/api/getUserAddresses');
getAllTokens();
fetchBlockchain();
