const DeviceRegistry = artifacts.require("DeviceRegistry");

module.exports = async function (deployer) {
  await deployer.deploy(DeviceRegistry);
  const registry = await DeviceRegistry.deployed();
  for (const id of ["dev1", "dev2", "dev3"]) {
    await registry.registerDevice(id);
  }
};
