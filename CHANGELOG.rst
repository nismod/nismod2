=========
Changelog
=========

Version 2.4.0
=============

Features:
- Add DAFNI wrappers and docker container image definitions

Fixes:
- Bump energy demand to 1.0.1
- Bump energy supply data
- Output aggregated EV trip starts and energy consumption
- Bump smif to 1.3.2


Version 2.3.1
=============

Fixes:
- Add hydrogen_trans to energy_supply_optimised and energy_supply_constrained SoS models


Version 2.3.0
=============

Features:
- Add peak adaptor to improve energy validation (see #169 and #173)
- Add energy functionality for energy supply-demand paper (see #164)
- Add demand-only runs for resilience study (see #166)

Fixes
- Transport functionality and config for DAFNI wrapper


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
