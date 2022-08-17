### Unreleased

**New**

- Added `Logger.add_scope()`, allowing addition of custom logging scopes. A new scope must be provided with a name and a value. (@MurdoMaclachlan)

**Enhancements**

- The `Logger` model now requires a config path for the program to be provided upon initialisation. Log files will be stored in `{config_path}/logs`. (@MurdoMaclachlan)
- Added an optional argument, `notify: bool` to `Logger.new()`, allowing a log message to be created and sent as a desktop notification in one function call. (@MurdoMaclachlan)
- Renamed `Logger.define_output_path()` to `Logger.__define_output_path()`, as it is only intended to be run from within the class. (@MurdoMaclachlan)

**Documentation**

- Added missing docstring for `Logger.clean()`. (@MurdoMaclachlan)

### 0.1.0

**New**

- Created initial program and documentation. (@MurdoMaclachlan)