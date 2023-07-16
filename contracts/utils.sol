pragma solidity ^0.8.17;

library Utils {
    function compare(string memory A, string memory B) internal pure returns(bool) {
        if (bytes(A).length != bytes(B).length)
            return false;
        if (keccak256(bytes(A)) != keccak256(bytes(B)))
            return false;
        uint length = bytes(A).length;
        for (uint i = 0; i < length; i++)
            if (bytes(A)[i] != bytes(B)[i])
                return false;
        return true;
    }
}