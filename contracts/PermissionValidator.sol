pragma solidity ^0.8.17;

contract PermissionValidator {
    address private creator;
    address[] private admins;

    constructor () {
        creator = msg.sender;
    }

    function permissionValidate(address sender) internal view returns(int) {
        if (creator == sender)
            return 2;
        uint length = admins.length;
        for (uint i = 0; i < length; i++)
            if (admins[i] == sender)
                return 1;
        return 0;
    }

    modifier isCreator(address sender){
        require (sender == creator, "sender should be creator");
        _;
    }

    function canUpdate(address sender) external view returns(bool){
        return (permissionValidate(sender) > 0);
    }

    function searchAdmin(address _addr) private view returns(int){
        uint length = admins.length;
        for (uint i = 0; i < length; i++)
            if (admins[i] == _addr)
                return int(i);
        return -1;
    }

    function remove(uint index) private {
        uint length = admins.length;
        if (index >= length)
            return;
        address temp = admins[length - 1];
        admins[length - 1] = admins[index];
        admins[index] = temp;
        admins.pop();
    }

    function addAdmin(address newAdmin) public isCreator(msg.sender) {
        if (searchAdmin(newAdmin) != -1)
            return;
        admins.push(newAdmin);
    }

    function removeAdmin(address _addr) public isCreator(msg.sender) {
        int index = searchAdmin(_addr);
        if (index < 0)
            return;
        remove(uint(index));
    }

    function isReady() public pure returns(string memory) {
        return "OK";
    }
}