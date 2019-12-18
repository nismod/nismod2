=========
Changelog
=========

Version 2.2.0
=============
Functionality:
- Migrate the nismod configuration to smif v1.0
- Add CONTRIBUTORS.md
- Add data download and preparation, link to Amazon S3
- Add install instructions and outline documentation
- Remove model submodules (document installation of numbered versions)
- Add water supply and demand models
- Add rail transport model
- Add et_module energy-transport adaptor
- Update energy supply and demand models
- Update digital model
- Update scenarios
- Update model wrappers to run new/updated models, add inputs, parameters, outputs

Bugs:
- Fix typos, bugs in wrappers, configuration files and data preparation scripts


Version 2.1.1
=============
Bugs:
- Repair transport_test model (wrapper paths, connect scenarios, inputs and outputs)


Version 2.1.0
=============
Functionality:
- Add digital_comms_test model
- Add transport_test model

Bugs:
- Repair energy_supply_test model (not all inputs linked to dependencies)


Version 2.0.0
=============
Functionality:
- Add energy_demand_test model
- Add energy_supply_test model
