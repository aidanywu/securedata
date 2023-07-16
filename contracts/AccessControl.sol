pragma solidity ^0.8.17;

import {Utils} from "./utils.sol";
import {PermissionValidator} from "./PermissionValidator.sol";

contract AccessControl{
    
    PermissionValidator private PV;
    mapping (string => string[]) private UserEntryMapping;

    constructor(PermissionValidator _PV) public {
        PV = _PV;
    }

    modifier isAdmin(address sender){
        require(PV.canUpdate(sender), "sender should be admins");
        _;
    }


    function addUserEntry(string memory userID, string memory entryID) public isAdmin(msg.sender) {
        int findResult = findEntryIndex(userID, entryID);
        if (findResult < 0)
            UserEntryMapping[userID].push(entryID);
    }

    function getUserEntry(string memory userID) public view returns(string[] memory arr, uint length) {
        return (UserEntryMapping[userID], UserEntryMapping[userID].length);
    }

    function findEntryIndex(string memory userID, string memory entryID) private view returns(int) {
        if (UserEntryMapping[userID].length == 0)
            return -1;
        uint length = UserEntryMapping[userID].length;
        for (uint i = 0; i < length; i++)
            if (Utils.compare(entryID, UserEntryMapping[userID][i]))
                return int(i);
        return -2;
    }


    function removeUserEntry(string memory userID, string memory entryID) public isAdmin(msg.sender) returns(int code) {
        int findResult = findEntryIndex(userID, entryID);
        if (findResult == -1){
            code = -1;
            return code;
        }
        if (findResult == -2){
            code = -2;
            return code;
        }

        /*
        uint length = UserEntryMapping[userID].length;
        for (uint i = uint(findResult); i < length - 1; i++)
            UserEntryMapping[userID][i] = UserEntryMapping[userID][i + 1];
        delete UserEntryMapping[userID][length - 1];
        UserEntryMapping[userID].length--;
        */

        uint length = UserEntryMapping[userID].length;
        string memory temp = UserEntryMapping[userID][length - 1];
        UserEntryMapping[userID][length - 1] = UserEntryMapping[userID][uint(findResult)];
        UserEntryMapping[userID][uint(findResult)] = temp;
        UserEntryMapping[userID].pop();

        code = 0;
        return code;
        
    }

    function removeAllEntry(string memory userID) public isAdmin(msg.sender)  {
        delete UserEntryMapping[userID];
    }

    function validateUserEntry(string memory userID, string memory EntryID) view public returns(bool) {
        int findResult = findEntryIndex(userID, EntryID);
        return (findResult >= 0);
    }

    function checkPV() public view returns(string memory) {
        return PV.isReady();
    }

}