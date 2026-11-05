// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract DeviceRegistry {
    address public admin;

    struct Device {
        bool registered;
        bool authorized;
        uint256 credit;
    }

    struct Action {
        string deviceId;
        string action;
        string reason;
        uint256 score;
        uint256 timestamp;
    }

    uint256 public constant INITIAL_CREDIT = 100;
    uint256 public constant PENALTY = 25;

    mapping(string => Device) public devices;
    Action[] public actions;

    event DeviceRegistered(string deviceId);
    event MitigationLogged(uint256 indexed id, string deviceId, string action, string reason, uint256 timestamp);
    event DeviceReinstated(string deviceId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function registerDevice(string calldata _id) external onlyAdmin {
        require(!devices[_id].registered, "already registered");
        devices[_id] = Device(true, true, INITIAL_CREDIT);
        emit DeviceRegistered(_id);
    }

    function isAuthorized(string calldata _id) external view returns (bool) {
        return devices[_id].authorized;
    }

    function logMitigation(
        string calldata _id,
        string calldata _action,
        string calldata _reason,
        uint256 _score
    ) external onlyAdmin {
        Device storage d = devices[_id];
        if (d.registered) {
            d.credit = d.credit > PENALTY ? d.credit - PENALTY : 0;
            if (d.credit == 0) {
                d.authorized = false;
            }
        }
        actions.push(Action(_id, _action, _reason, _score, block.timestamp));
        emit MitigationLogged(actions.length - 1, _id, _action, _reason, block.timestamp);
    }

    function reinstate(string calldata _id) external onlyAdmin {
        require(devices[_id].registered, "unknown device");
        devices[_id].credit = INITIAL_CREDIT;
        devices[_id].authorized = true;
        emit DeviceReinstated(_id);
    }

    function actionCount() external view returns (uint256) {
        return actions.length;
    }
}
