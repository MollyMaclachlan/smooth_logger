# smooth_logger

A simple logger made primarily for my own personal use. Was made out of a combination of necessity and being so lazy that I overflowed into being productive and instead of searching for a library that suited my needs, I wrote my own.

## Installation

smooth_logger can be installed through pip. Either download the latest release from Codeberg/GitHub, or do `pip install smooth_logger` to install from PyPi. For the latest commits, check the `dev` branches on the repositories.

smooth_logger is currently devloped using Python 3.11, but should work with Python 3.5 and up. A minimum of 3.5 is required due to the project's use of type hinting, which was introduced in that version.

smooth_logger supports Linux, macOS and Windows.

## Usage

Usage of smooth-logger is, as it should be, quite simple.

The `Logger` model provides a number of methods for your use:

- `Logger.add_scope()` adds a new scope.
- `Logger.clean()` erases all log entries currently in memory.
- `Logger.edit_scope()` modifies the category of an existing scope.
- `Logger.get()` allows you to retrieve either the most recent log entry or all log entries, optionally filtered by scope.
- `Logger.get_time()` returns the full date & time, or optionally just the date, in ISO-8601 formatting.
- `Logger.init_bar()` initialises the `ProgressBar` model imported from the `smooth_progress` dependency.
- `Logger.notify()` sends a desktop notification using the `plyer` dependency.
- `Logger.new()` creates and, depending on scope, prints a new log entry.
- `Logger.output()` saves all log entries of appropriate scope to the log file and cleans the log array for the next group of log entries. A new log file is created for each new day. This method only attempts to create or update the log file if there are entries of an appropriate scope to be written to it; if there are none, it just executes `Logger.clean()`.
- `Logger.remove_scope()` removes an existing scope.

### Initialisation

Here is a simple example showing the initialisation of the logger:

```py
import smooth_logger

Log = smooth_logger.Logger("Example")
Log.new("This is a log message!", "INFO")
```

In the case above, the logger will automatically create a folder called `Example` under `~.config` on Linux and macOS, or `APPDATA\Roaming` on Windows, which will contain a subfolder called `logs`, where the log files will be saved.

You can use the format below to provide a custom location:

```py
Log = smooth_logger.Logger("Example", config_path="~/this/is/an/example")
```

In this case, logs would be stored under, `~/this/is/an/example/logs`.

### Scopes

Every log message is associated with a scope. This is an all-caps prefix to the message that should, in a single word, communicate what the message is about. The default scopes available, along with their suggested use cases, are:

- DEBUG: Information for debugging the program.
- ERROR: Errors that the program can recover from but impact functionality or performance.
- FATAL: Errors that mean the program must continue; handled crashes.
- INFO: General information for the user.
- WARNING: Things that have no immediate impact to functionality but could cause errors later on.

You can also use the value "NOSCOPE" to indicate that a message should be printed without a prefixed scope. Messages with no scope are printed to the console, not saved to the output file, and are not accompanied by a timestamp.

### Categories

When initialising the Logger, you can optionally provide categories to associate with each scope:

- DISABLED (will not print to console or save to log file)
- ENABLED (will print to console but not save to log file)
- MAXIMUM (will print to console and save to log file)

Categories are accessed like so:

```py
from smooth_logger.enums import Categories

Categories.ENABLED
```

By default, the DEBUG scope is disabled, the INFO scope is enabled, and the ERROR, FATAL and WARNING scopes are all set to maximum.

### Customising scopes

You can create custom scopes using the `Logger.add_scope()` method. These are currently instance-specific and not hard saved in any way. A simple usage of this is as follows:

```py
Log.add_scope("NEWSCOPE", Categories.ENABLED)
```

Similarly, you can use `Logger.edit_scope()` to modify the category of an existing scope (for the specific instance only), like so:

```py
Log.edit_scope("DEBUG", Categories.ENABLED)
```

The above statement could, for example, be used to temporarily enable debug statements if an error is detected.

Only the categories defined in the `Categories` enum will be recognised; attempting to pass anything else as a category will prompt a warning, and the scope will not be added/edited.

Finally, you can remove any scope with the following method:

```py
Log.remove_scope("DEBUG")
```

It is recommended to be careful with this method. Removing scopes, like adding or editing them, is ephemeral and won't be hard-saved anywhere, but removing a scope during run-time will produce warnings if you attempt to use that scope anywhere in your program.

## Roadmap

- Rework `Logger.get()` to allow passing of a specific number of log values to be fetched. If these values exceed the number in the log, all matching log values should be returned, and a warning should be issued (but not returned).

- Possibly replace some internal warnings with Exceptions so they can be more easily-handled by end-user programs.

- Add a category that saves to the log file but doesn't print to the console.