from datetime import datetime
from os import environ, makedirs
from os.path import expanduser, isdir
from plyer import notification
from smooth_progress import ProgressBar
from sys import platform
from time import time
from typing import Dict, List, Union


class Logger:
    """Class for controlling the entirety of logging. The logging works on a scope-based
    system where (almost) every message has a defined scope, and the scopes are each
    associated with a specific value between 0 and 2 inclusive. The meanings of the
    values are as follows:

    0: disabled, do not print to console or save to log file
    1: enabled, print to console but do not save to log file
    2: maximum, print to console and save to log file
    """
    def __init__(
        self: object, program_name: str, debug: int = 0, error: int = 2, fatal: int = 2,
        info: int = 1, warning: int = 2
    ) -> None:
        self.bar: Union[ProgressBar, None] = None
        self.__is_empty: bool = True
        self.__log: List[LogEntry] = []
        self.__notifier: object = notification
        self.__program_name: str = program_name
        self.__scopes: Dict[str, int] = {
            "DEBUG":   debug,   # information for debugging the program
            "ERROR":   error,   # errors the program can recover from
            "FATAL":   fatal,   # errors that mean the program cannot continue
            "INFO":    info,    # general information for the user
            "WARNING": warning  # things that could cause errors later on
        }
        self.__write_logs = False
        self.__path: str = self.define_output_path(expanduser("~"), platform)

    def __define_output_path(self: object, home: str, os: str) -> str:
        """Detects OS and defines the appropriate save paths for the config and data.
        Exits on detecting an unspported OS. Supported OSes are: Linux, MacOS, Windows.

        :arg home: string; the user's home folder
        :arg os: string; the user's operating system

        :return: a single string dict containing the newly-defined output path
        """
        os = "".join(list(os)[:3])

        # Route for a supported operating system
        if os in ["dar", "lin", "win"]:

            path = (
                environ["APPDATA"] + f"\\{self.__program_name}\logs"
                if os == "win" else
                f"{home}/.config/{self.__program_name}/logs"
            )

            # Create any missing directories
            if not isdir(path):
                self.new(f"Making path: {path}", "INFO")
                makedirs(path, exist_ok=True)
            return path

        # Exit if the operating system is unsupported
        else:
            print(f"FATAL: Unsupported operating system: {os}, exiting.")
            exit()

    def add_scope(self: object, name: str, value: int) -> bool:
        """Adds a new logging scope for use with log entries. Users should be careful
        when doing this; custom scopes would be best added immediately following
        initialisation. If a 'Logger.new()' call is run before the scope it uses is
        added, it will generate a warning.

        The recommended format for scope names is all uppercase, with no spaces or
        underscores. Custom scopes are instance specific ad not hard saved.

        :arg name: string; the name of the new scope.
        :arg default_value: int; from 0 to 2, the default value of the new scope.

        :return: A boolean indicating the success or failure of adding the new scope.
        """
        if name in self.__scopes.keys():
            self.new(
                f"Attempt was made to add new scope with name {name}, but scope with "
                + "this name already exists.",
                "WARNING"
            )
            return False
        else:
            self.__scopes[name] = value
        return True

    def clean(self: object) -> None:
        """Empties log array, amending '__is_empty' to True and '__write_logs' to False.
        """
        del self.__log[:]
        self.__is_empty = True
        self.__write_logs = False

    def get(
            self: object, mode: str = "all", scope: str = None
        ) -> Union[List[str], str, None]:
        """Returns item(s) in the log. What entries are returned can be controlled by
        passing optional arguments.

        :arg mode: optional, string; options are 'all' and 'recent'.
        :arg scope: optional, string; if passed, only entries with matching scope will
          be returned.

        :return: a single log entry (string), list of log entries (string array), or an
          empty string on a failure.
        """
        if self.__is_empty:
            pass
        elif scope is None:
            # Tuple indexing provides a succint way to determine what to return
            return (self.__log, self.__log[len(self.__log)-1])[mode == "recent"]
        else:
            # Return all log entries with a matching scope
            if mode == "all":
                data = []
                for i in self.__log:
                    if i.scope == scope:
                        data.append(i)
                if data:
                    return data
            # Return the most recent log entry with a matching scope; for this purpose,
            # we reverse the list then iterate through it.
            elif mode == "recent":
                for i in self.__log.reverse():
                    if i.scope == scope:
                        return self.__log[i]
            else:
                self.new("Unknown mode passed to Logger.get().", "WARNING")
        # Return an empty string to indicate failure if no entries were found
        return ""

    def get_time(self: object, method: str = "time") -> str:
        """Gets the current time and parses it to a human-readable format.

        :arg method: string; the method to calculate the timestamp; either 'time' or
          'date'.

        :return: a single date string formatted either 'YYYY-MM-DD HH:MM:SS' or
          'YYYY-MM-DD'
        """
        if method in ["time", "date"]:
            return datetime.fromtimestamp(time()).strftime(
                ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S")[method == "time"]
            )
        else:
            print("ERROR: Bad method passed to Logger.get_time().")
            return ""

    def init_bar(self: object, limit: int) -> None:
        """Initiate and open the progress bar.

        :arg limit: int; the number of increments it should take to fill the bar.
        """
        self.bar = ProgressBar(limit=limit)
        self.bar.open()

    def notify(self: object, message: str) -> None:
        """Display a desktop notification with a given message.

        :arg message: string; the message to display in the notification.
        """
        self.__notifier.notify(title=self.__program_name, message=message)

    def new(
            self: object,
            message: str, scope: str, do_not_print: bool = False
        ) -> bool:
        """Initiates a new log entry and prints it to the console. Optionally, if
        do_not_print is passed as True, it will only save the log and will not print
        anything (unless the scope is 'NOSCOPE'; these messages are always printed).

        :arg message: string; the messaage to log.
        :arg scope: string; the scope of the message (e.g. debug, error, info).
        :arg do_not_print: optional, bool; False by default.

        :return: boolean success status.
        """
        if scope in self.__scopes or scope == "NOSCOPE":
            # TODO: sperate some of this into submethods

            # Setup variables
            output = (self.__scopes[scope] == 2) if scope != "NOSCOPE" else False
            isBar: bool = (self.bar is not None) and self.bar.opened

            # Create and save the log entry
            if isBar and len(message) < len(self.bar.state):
                message += " " * (len(self.bar.state) - len(message))
            entry = LogEntry(message, output, scope, self.get_time())
            self.__log.append(entry)

            # Print the message, if required
            if scope == "NOSCOPE":
                print(entry.rendered)
            elif self.__scopes[scope]:
                print(entry.rendered if not do_not_print else None)

            # Re-print bar, if required
            if isBar:
                print(self.bar.state, end="\r", flush=True)

            # Amend boolean states
            if not self.__write_logs:
                self.__write_logs = output
            self.__is_empty = False

            return True
        else:
            self.new("Unknown scope passed to Logger.new()", "WARNING")
        return False

    def output(self: object) -> None:
        """Write all log entries with scopes set to save to a log file in a data folder
        in the working directory, creating the folder and file if they do not exist.
        The log files are marked with the date, so each new day, a new file will be
        created.
        """
        if self.__write_logs:
            with open(
                f"{self.__path}/log-{self.get_time(method='date')}.txt", "at+"
            ) as log_file:
                for line in self.__log:
                    if line.output:
                        log_file.write(line.rendered + "\n")
        self.clean()


class LogEntry:
    """Represents a single entry within the log, storing its timestamp, scope and
    message. This makes it easier to select certain log entries using the
    Logger.get() method.
    """
    def __init__(self: object, message: str, output: bool, scope: str, timestamp: str):
        self.message = message
        self.output = output
        self.scope = scope
        self.timestamp = timestamp
        self.rendered = (
            f"[{timestamp}] {scope}: {message}"
            if scope != "NOSCOPE" else
            f"{message}"
        )