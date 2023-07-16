pragma solidity ^0.8.17;

import {PermissionValidator} from "./PermissionValidator.sol";
import {DateTime} from "./DateTime.sol";

contract AccessRecord{
    struct Record{
        string userID;
        string entryID;
        uint time;
    }
    Record[] private recordTable;
    PermissionValidator private PV;

    constructor (PermissionValidator _PV) {
        PV = _PV; 
    }

    modifier isAdmin(address sender) {
        require(PV.canUpdate(sender), "sender should be admin");
        _;
    }

    function addRecord(string memory _userID, string memory _entryID) public isAdmin(msg.sender){
        recordTable.push(Record(_userID, _entryID, block.timestamp));
        //recordTable.push(Record(_userID, _entryID, 0));
    }

    function removeOutDateRecord() public isAdmin(msg.sender) returns(uint) {
        
        uint cur_time = block.timestamp;
        //uint cur_time = 0;
        uint16 cur_year = DateTime.getYear(cur_time);
        uint bp = recordTable.length;
        for (uint i = 0; i < recordTable.length; i++){
            if (DateTime.getYear(recordTable[i].time) > cur_year - 1){
                bp = i;
                break;
            }
        }
        if (bp == recordTable.length)
            return 0;
        for (uint i = bp; i < recordTable.length; i++)
            recordTable[i - bp] = recordTable[i];
        for (uint i = 0; i < bp; i++)
            recordTable.pop();
        return bp;
        
    }

    function showAll() view public returns (Record[] memory) {
        return recordTable;
    }

    function checkPV() view public returns (string memory) {
        return PV.isReady();
    }
}
