# VUT-MPA_MOK-project

Project to course Modern Cryptography at Brno University of Technology, Faculty of Electrical Engineering and
Communication.

Project is supposed to show a demo of implementation of Smart Non-Fungible Tokens. Research was not done by me, I do not
own any rights to the underlying research.

Smart NFT paper can be found here https://www.mdpi.com/1424-8220/21/9/3119
Solidity implementation of this project here https://github.com/Hardblock-IMSE/Smart-Non-Fungible-Token

**Note:** I do not recommend to try request one API more than once at a time. It might happen that the server's state of
memory is going to get corrupted, because of concurrency.

## Build Dockerfile and run docker image
Build:
```commandline
docker build -t mok_project:latest <PATH_TO_PROJ_FOLDER>
```

Run image as container:
```commandline
docker run -p 127.0.0.1:8000:8000/tcp mok_project:latest
```

Stop all docker containers:
```commandline
docker container stop $(docker container ps -a -q)
```

## Available APIs:
* Blockchain actions:
  * [GET] **/api/getUserAddresses** (no parameters on input)
  * [GET] **/api/getOwnerAddresses** (no parameters on input)
    * both of these APIs above will respond with ETH addresses created by the other APIs below
  * [POST] **/api/createNewOwnerAddresses** (\<int:count\> parameter)
  * [POST] **/api/createNewUserAddresses** (\<int:count\> parameter)
    * both of the APIs above create ETH addresses based on param count
  * [PUT] **/api/setBlockchainDifficulty** (\<int:difficulty\> parameter)
    * sets the blockchain difficulty (how many zeroes as a prefix of the block hash)
  * [GET] **/api/getBlockchain** (no parameters on input)
    * gets the whole blockchain
  * [PUT] **/api/computeNewBlock**  (no parameters on input)
    * computes a new block and appends it to the blockchain
* Transactions
  * [POST] **/api/postTransaction** (\<str:sender\>, \<str:recipient\>, \<int:amount\> parameters)
    * signs and posts a regular transaction to the mempool
  * **_NOT DONE_** [GET] **/api/verifyTransaction** (\<str:claimer\>, \<str:transactionHash\> parameters)
    * returns a boolean if anyone claims has the rights to the transaction
* Smart contract (NFTs) actions:
  * [POST] **/api/createToken** (\<int:timeout\>, \<str:ownerAddress\> parameters)
    * creates an NFT with specified timeout and owner. Puts it in a transaction and sends it to the mempool
  * [GET] **/api/getAllTokens** (no parameters on input)
    * gets all created NFTs and their info
  * [PUT] **/api/transferNFTOwner** (\<str:newOwnerAddress\>, \<str:ownerAddress\>, \<int:tokenId\> parameters)
    * transfers an NFT owner to a new one. Puts the change in a transaction and sends it to the mempool
  * [PUT] **/api/setNFTUser** (\<str:newUserAddress\>, \<str:ownerAddress\>, \<int:tokenId\>, \<bool:ignoreUserCheck\> parameters)
    * sets a user of the NFT. Only owner of the token can do this action
    * ignoreUserCheck is available because the owner can also be a user of the token
  * [PUT] **/api/engageNFTUser** (\<str:userAddress\>, \<int:tokenId\> parameters)
  * [PUT] **/api/engageNFTOwner** (\<str:ownerAddress\>, \<int:tokenId\> parameters)
    * the two PUT methods above engage the token with user/owner (basically changes the status of token)
