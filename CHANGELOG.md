### Unreleased

**New**

- Added `Logger.add_scope()`, allowing addition of custom logging scopes. A new scope must be provided with a name and a value. (@MurdoMaclachlan)
- Added `Logger.edit_scope()`, allowing existing logging scopes to have their value changed during run-time. (@MurdoMaclachlan)

**Enhancements**

- The `Logger` model now requires a config path for the program to be provided upon initialisation. Log files will be stored in `{config_path}/logs`. (@MurdoMaclachlan)
- Added an optional argument, `notify: bool` to `Logger.new()`, allowing a log message to be created and sent as a desktop notification in one function call. (@MurdoMaclachlan)
- Renamed `Logger.define_output_path()` to `Logger.__create_log_folder()`. (@MurdoMaclachlan)

**Documentation**

- Added missing docstring for `Logger.clean()`. (@MurdoMaclachlan)
- Added syntax highlighting for README code example. (@MurdoMaclachlan)

### 0.1.0

**New**

- Created initial program and documentation. (@MurdoMaclachlan)