# BitBlender Scripts

## Folder Structure

There are several subfolders.

`codegen_scripts`:
- This contains the code-generation scripts, which can be used to generate BitBlender configurations (as in, hardware configurations).

`config_selection`:
- This contains `config_sel.py`, which implements the Auto Design-Space Explorer (AutoDSE). This is used to suggest several BitBlender configurations, given an algorithmic configuration.

`PerfModel_Scripts`:
- This contains `cycles_perfmodel.py`, which estimates the "efficiency" of a given dynamically-scheduled BitBlender configuration.
  This is NOT meant to be used by an end-user - it is used by the `config_selection` scripts.

