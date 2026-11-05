
const SecurityEventLog = artifacts.require("SecurityEventLog");

module.exports = function (deployer) {
    deployer.deploy(SecurityEventLog);
};
