from datetime import datetime
from os import makedirs
from os.path import isdir
from plyer import notification
from smooth_progress import ProgressBar
from time import time
from LogEntry import LogEntry

from plyer.facades import Notification
from typing import Dict, List, Union


class Logger:
    """
    Class for controlling the entirety of logging. The logging works on a scope-based system where
    (almost) every message has a defined scope, and the scopes are each associated with a specific
    value between 0 and 2 inclusive. The meanings of the values are as follows:

    0: disabled, do not print to console or save to log file
    1: enabled, print to console but do not save to log file
    2: maximum, print to console and save to log file
    """
    def __init__(self,
                 program_name: str,
                 config_path: str,
                 debug: int = 0,
                 error: int = 2,
                 fatal: int = 2,
                 info: int = 1,
                 warning: int = 2) -> None:
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

    def __create_log_entry(self, message: str, output: bool, scope: str) -> LogEntry:
        """
        Creates a new log entry from given settings and appends it to the log.

        :param message: the log message
        :param output: whether the message should be output to the log file
        :param scope: the scope of the message

        :returns: the created log entry
        """
        entry: LogEntry = LogEntry(message, output, scope, self.__get_time())
        self.__log.append(entry)
        return entry

    def __create_log_folder(self) -> None:
        """
        Creates the folder that will contain the log files.
        """
        if not isdir(self.__output_path):
            print(f"Making path: {self.__output_path}")
            makedirs(self.__output_path, exist_ok=True)
    
    def __display_log_entry(self,
                            entry: LogEntry,
                            scope: str,
                            notify: bool,
                            is_bar: bool,
                            print_to_console: bool = True) -> None:
        """
        Displays a given log entry as appropriate using further given settings.

        :param entry: the entry to display
        :param scope: the scope of the entry
        :param notify: whether to show a desktop notification for the entry
        :param is_bar: whether the progress bar is active
        :param console: whether the message should be printed to the console
        """
        if scope == "NOSCOPE" or (self.__scopes[scope] > 0 and print_to_console):
            print(entry.rendered)
        if is_bar:
            print(self.bar.state, end="\r", flush=True)
        if notify:
            self.notify(entry.message)

    def __get_time(self, method: str = "time") -> str:
        """
        Gets the current time and parses it to a human-readable format; either
        'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'.

        :param method: the format of the timestamp; either 'time' or 'date'.

        :returns: a single date string
        """
        if method in ["time", "date"]:
            return datetime.fromtimestamp(time()).strftime(
                ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S")[method == "time"]
            )
        else:
            self.new("Bad method passed to Logger.get_time().", "ERROR")
            return ""

    def add_scope(self, name: str, value: int) -> bool:
        """
        Adds a new logging scope for use with log entries. Users should be careful when doing this;
        custom scopes would be best added immediately following initialisation. If a 'Logger.new()'
        call is made before the scope it uses is added, it will generate a warning.

        The recommended format for scope names is all uppercase, with no spaces or underscores.
        Custom scopes are instance specific and not hard saved.

        :param name: the name of the new scope
        :param value: the default value of the new scope (0-2)

        :return: a boolean sucess status
        """
        if name in self.__scopes.keys():
            self.new(
                f"Attempt was made to add new scope with name {name}, but scope with this name "
                + "already exists.",
                "WARNING"
            )
        else:
            self.__scopes[name] = value
            return True
        return False

    def clean(self) -> None:
        """
        Empties log array. Any log entries not saved to the output file will be lost.
        """
        del self.__log[:]
        self.__is_empty = True
        self.__write_logs = False

    def edit_scope(self, name: str, value: int) -> bool:
        """
        Edits an existing scope's value. Edited values are instance specific and not hard saved.

        :param name: the name of the scope to edit
        :param value: the new value of the scope (0-2)

        :returns: a boolean success status
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

    def get(self, mode: str = "all", scope: str = None) -> Union[List[LogEntry], LogEntry]:
        """
        Returns item(s) in the log. The entries returned can be controlled by passing optional
        arguments.

        If no entries match the query, nothing will be returned.

        :param mode: optional; 'all' for all log entries or 'recent' for only the most recent one
        :param scope: optional; if passed, only entries matching its value will be returned

        :returns: a single log entry or list of log entries, or nothing
        """
        if self.__is_empty:
            pass
        elif scope is None:
            return (self.__log, self.__log[-1])[mode == "recent"]
        else:
            # return all log entries matching the query
            if mode == "all":
                data: list[LogEntry] = []
                for i in self.__log:
                    if scope is None or i.scope == scope:
                        data.append(i)
                if data:
                    return data
            # iterate through the log in reverse to find the most recent entry matching the query
            elif mode == "recent":
                for i in range(len(self.__log)-1, 0):
                    if scope is None or self.__log[i].scope == scope:
                        return self.__log[i]
            else:
                self.new("Unknown mode passed to Logger.get().", "WARNING")

    def init_bar(self, limit: int) -> None:
        """
        Initiate and open the progress bar.

        :param limit: the number of increments it should take to fill the bar
        """
        self.bar = ProgressBar(limit=limit)
        self.bar.open()

    def new(self,
            message: str,
            scope: str,
            print_to_console: bool = False,
            notify: bool = False) -> bool:
        """
        Initiates a new log entry and prints it to the console. Optionally, if do_not_print is
        passed as True, it will only save the log and will not print anything (unless the scope is
        'NOSCOPE'; these messages are always printed).

        :param message: the log message
        :param scope: the scope of the message
        :param print_to_console: optional, default True; whether the message should be printed to
                                 the console
        :param notify: optional, default False; whether the message should be displayed as a
                       desktop notification

        :returns: a boolean success status
        """
        if scope in self.__scopes or scope == "NOSCOPE":
            output: bool = (self.__scopes[scope] == 2) if scope != "NOSCOPE" else False
            is_bar: bool = (self.bar is not None) and self.bar.opened

            # if the progress bar is enabled, append any necessary empty characters to the message
            # to completely overwrite it upon output
            if is_bar and len(message) < len(self.bar.state):
                message += " " * (len(self.bar.state) - len(message))
            
            entry: LogEntry = self.__create_log_entry(message, output, scope)
            self.__display_log_entry(entry, scope, notify, print_to_console, is_bar)

            self.__write_logs = self.__write_logs or output
            self.__is_empty = False

            return True
        else:
            self.new("Unknown scope passed to Logger.new()", "WARNING")
        return False

    def notify(self, message: str) -> None:
        """
        Displays a desktop notification with a given message.

        :param message: the message to display
        """
        self.__notifier.notify(title=self.__program_name, message=message)

    def output(self) -> None:
        """
        Writes all log entries with appropriate scopes to the log file. If the output path for the
        log file does not exist, it is created.

        Log files are marked with the date, so each new day, a new file will be created.
        """
        if self.__write_logs:
            with open(f"{self.__output_path}/log-{self.__get_time(method='date')}.txt",
                      "at+") as log_file:
                for line in self.__log:
                    if line.output:
                        log_file.write(line.rendered + "\n")
        self.clean()
