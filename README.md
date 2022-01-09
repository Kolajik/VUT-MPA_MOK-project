# VUT-MPA_MOK-project

Project to course Modern Cryptography at Brno University of Technology, Faculty of Electrical Engineering and
Communication.

Project is supposed to show a demo of implementation of Smart Non-Fungible Tokens. Research was not done by me, I do not
own any rights to the underlying research.

Smart NFT paper can be found here https://www.mdpi.com/1424-8220/21/9/3119
Solidity implementation of this project here https://github.com/Hardblock-IMSE/Smart-Non-Fungible-Token

**Note:** I do not recommend to try request one API more than once at a time. It might happen that the server's state of
memory is going to get corrupted, because of concurrency.

Available APIs:
* /api/getETHUsrAddress (no parameters on input)
* /api/createNewUserAddresses/ (\<int:count\> parameter)
* /api/createNewUserAddresses/ (\<int:count\> parameter)
* 