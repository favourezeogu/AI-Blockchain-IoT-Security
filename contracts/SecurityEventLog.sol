
 // SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SecurityEventLog {

    address public admin;
    uint256 public eventCount;

    event SecurityEventLogged(
        uint256 indexed eventId,
        string deviceId,
        string action,
        string reason,
        uint256 score,
        bool dryRun,
        uint256 timestamp
    );

    constructor() {
        admin = msg.sender;
    }

    function logSecurityEvent(
        string calldata deviceId,
        string calldata action,
        string calldata reason,
        uint256 score,
        bool dryRun
    ) external {

        require(msg.sender == admin, "Only admin");

        uint256 id = eventCount;
        eventCount += 1;

        emit SecurityEventLogged(
            id,
            deviceId,
            action,
            reason,
            score,
            dryRun,
            block.timestamp
        );
    }
}
