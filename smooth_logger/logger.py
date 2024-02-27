from datetime import datetime
from os import makedirs
from os.path import isdir
from plyer import notification
from smooth_progress import ProgressBar
from time import time

from plyer.facades import Notification
from typing import Dict, List, Union


class LogEntry:
    """Represents a single entry within the log, storing its timestamp, scope and
    message. This makes it easier to select certain log entries using the
    Logger.get() method.
    """
    def __init__(
        self: object, message: str, output: bool, scope: str, timestamp: str
    ) -> None:
        self.message = message
        self.output = output
        self.scope = scope
        self.timestamp = timestamp
        self.rendered = (
            f"[{timestamp}] {scope}: {message}"
            if scope != "NOSCOPE" else
            f"{message}"
        )


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
        self, program_name: str, config_path: str, debug: int = 0, error: int = 2,
        fatal: int = 2, info: int = 1, warning: int = 2
    ) -> None:
        self.bar: ProgressBar = ProgressBar()
        self.__is_empty: bool = True
        self.__log: List[LogEntry] = []
        self.__notifier: Notification = notification
        self.__output_path: str = f"{config_path}/logs"
        self.__program_name: str = program_name
        self.__scopes: Dict[str, int] = {
            "DEBUG":   debug,   # information for debugging the program
            "ERROR":   error,   # errors the program can recover from
            "FATAL":   fatal,   # errors that mean the program cannot continue
            "INFO":    info,    # general information for the user
            "WARNING": warning  # things that could cause errors later on
        }
        self.__write_logs = False
        self.__create_log_folder()

    def __create_log_folder(self) -> None:
        if not isdir(self.__output_path):
            print(f"Making path: {self.__output_path}")
            makedirs(self.__output_path, exist_ok=True)

    def __get_time(self, method: str = "time") -> str:
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

    def add_scope(self, name: str, value: int) -> bool:
        """Adds a new logging scope for use with log entries. Users should be careful
        when doing this; custom scopes would be best added immediately following
        initialisation. If a 'Logger.new()' call is run before the scope it uses is
        added, it will generate a warning.

        The recommended format for scope names is all uppercase, with no spaces or
        underscores. Custom scopes are instance specific and not hard saved.

        :arg name: string; the name of the new scope.
        :arg value: int; from 0 to 2, the default value of the new scope.

        :return: A boolean indicating the success or failure of adding the new scope.
        """
        if name in self.__scopes.keys():
            self.new(
                f"Attempt was made to add new scope with name {name}, but scope with "
                + "this name already exists.",
                "WARNING"
            )
        else:
            self.__scopes[name] = value
            return True
        return False

    def clean(self) -> None:
        """Empties log array, amending '__is_empty' to True and '__write_logs' to False.
        """
        del self.__log[:]
        self.__is_empty = True
        self.__write_logs = False

    def edit_scope(self, name: str, value: int) -> bool:
        """Edits an existing logging scope's value. Edited values are instance specific
        and not hard saved.

        :arg name: string; the name of the scope to edit.
        :arg value: int; from 0 to 2, the new value of the scope.

        :return: A boolean indicating the success or failure of editing the scope.
        """
        if name in self.__scopes.keys():
            self.__scopes[name] = value
            return True
        else:
            self.new(
                f"Attempt was made to edit a scope with name {name}, but no scope with "
                + "this name exists.",
                "WARNING"
            )
        return False

    def get(self, mode: str = "all", scope: str = None) -> Union[
        List[LogEntry], LogEntry, str
    ]:
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
            # Tuple indexing provides a succinct way to determine what to return
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

                for i in range(len(self.__log)-1, 0):
                    if self.__log[i].scope == scope:
                        return self.__log[i]
            else:
                self.new("Unknown mode passed to Logger.get().", "WARNING")
        # Return an empty string to indicate failure if no entries were found
        return ""

    def init_bar(self, limit: int) -> None:
        """Initiate and open the progress bar.

        :arg limit: int; the number of increments it should take to fill the bar.
        """
        self.bar = ProgressBar(limit=limit)
        self.bar.open()

    def new(
            self, message: str, scope: str, do_not_print: bool = False,
            notify: bool = False
        ) -> bool:
        """Initiates a new log entry and prints it to the console. Optionally, if
        do_not_print is passed as True, it will only save the log and will not print
        anything (unless the scope is 'NOSCOPE'; these messages are always printed).

        :arg message: string; the message to log.
        :arg scope: string; the scope of the message (e.g. debug, error, info).
        :arg do_not_print: optional, bool; False by default. Passing as True causes the
          message not to be printed to the console, regardless of scope.
        :arg notify: optional, bool; False by default. Passing as True will display the
          message as a desktop notification.

        :return: boolean success status.
        """
        if scope in self.__scopes or scope == "NOSCOPE":
            # TODO: separate some of this into sub-methods

            # Setup variables
            output = (self.__scopes[scope] == 2) if scope != "NOSCOPE" else False
            isBar: bool = (self.bar is not None) and self.bar.opened

            # Create and save the log entry
            if isBar and len(message) < len(self.bar.state):
                message += " " * (len(self.bar.state) - len(message))
            entry = LogEntry(message, output, scope, self.__get_time())
            self.__log.append(entry)

            # Print the message, if required
            if scope == "NOSCOPE" or (self.__scopes[scope] > 0 and not do_not_print):
                print(entry.rendered)

            if isBar:
                print(self.bar.state, end="\r", flush=True)
            if notify:
                self.notify(message)

            # Amend boolean states
            self.__write_logs = self.__write_logs or output
            self.__is_empty = False

            return True
        else:
            self.new("Unknown scope passed to Logger.new()", "WARNING")
        return False

    def notify(self, message: str) -> None:
        """Display a desktop notification with a given message.

        :arg message: string; the message to display in the notification.
        """
        self.__notifier.notify(title=self.__program_name, message=message)

    def output(self) -> None:
        """Write all log entries with scopes set to save to a log file in a data folder
        in the working directory, creating the folder and file if they do not exist.
        The log files are marked with the date, so each new day, a new file will be
        created.
        """
        if self.__write_logs:
            with open(
                f"{self.__output_path}/log-{self.__get_time(method='date')}.txt", "at+"
            ) as log_file:
                for line in self.__log:
                    if line.output:
                        log_file.write(line.rendered + "\n")
        self.clean()
