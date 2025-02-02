import re
from typing import Optional
from typing import List, Dict
from app.models.error_details import ErrorDetail


class LogService:
    ERROR_PATTERNS = {
        "python": r"Traceback \(most recent call last\):[\s\S]+?\n\w+Error: .+",
        "javascript": r"(?:TypeError|ReferenceError|SyntaxError):.+",
        "api": r"(?:4\d{2}|5\d{2}) (?:Error|NOT_FOUND|BAD_REQUEST):.+",
    }

    @staticmethod
    def parse_logs(logs: str) -> List[Dict]:
        """
        Parses a string containing log data into a list of dictionaries.

        Each line of the log string is parsed to extract relevant information
        such as timestamp, content, and log level, which are stored in a dictionary.
        These dictionaries are then collected into a list representing all log entries.

        Args:
            logs (str): A string containing the log data, with each line representing a log entry.

        Returns:
            List[Dict]: A list of dictionaries, each representing a parsed log entry.

        Raises:
            Exception: If parsing of the logs fails.
        """

        try:
            log_entries = []
            lines = logs.split("\n")

            for line in lines:
                if line.strip():
                    entry = LogService._parse_log_line(line)
                    if entry:
                        log_entries.append(entry)

            return log_entries
        except Exception as e:
            raise Exception(f"Log parsing failed: {str(e)}")

    @staticmethod
    def analyze_logs(logs: str) -> Dict:
        """
        Analyzes a string containing log data and returns a dictionary with the following information:

        - total_entries: The total number of log entries.
        - error_count: The number of error log entries.
        - errors: A list of dictionaries, each describing an error log entry.
        - timeline: A list of dictionaries, each representing a log entry with a timestamp.
        - summary: A dictionary with information about the log, such as the distribution of log levels.

        Args:
            logs (str): A string containing the log data, with each line representing a log entry.

        Returns:
            Dict: A dictionary containing the analysis of the log data.

        Raises:
            Exception: If analysis of the logs fails.
        """

        try:
            parsed_logs = LogService.parse_logs(logs)
            errors = LogService.extract_errors(logs)

            return {
                "total_entries": len(parsed_logs),
                "error_count": len(errors),
                "errors": errors,
                "timeline": LogService._create_timeline(parsed_logs),
                "summary": LogService._create_summary(parsed_logs),
            }
        except Exception as e:
            raise Exception(f"Log analysis failed: {str(e)}")

    @staticmethod
    def extract_errors(logs: str) -> List[ErrorDetail]:
        """
        Extracts errors from a string containing log data and returns a list of ErrorDetail objects.

        Args:
            logs (str): A string containing the log data, with each line representing a log entry.

        Returns:
            List[ErrorDetail]: A list of ErrorDetail objects, each describing an error log entry.

        Raises:
            Exception: If extraction of errors from the logs fails.
        """

        errors = []
        for error_type, pattern in LogService.ERROR_PATTERNS.items():
            matches = re.finditer(pattern, logs, re.MULTILINE)
            for match in matches:
                error_text = match.group(0)
                errors.append(
                    ErrorDetail(
                        error_type=error_type,
                        message=error_text,
                        line_number=LogService._extract_line_number(error_text),
                        suggestion=LogService._generate_suggestion(
                            error_type, error_text
                        ),
                    )
                )
        return errors

    @staticmethod
    def _parse_log_line(line: str) -> Dict:
        """
        Parses a single log line and returns a dictionary containing the log entry's timestamp, content, and level.

        Args:
            line (str): A single line of the log data.

        Returns:
            Dict: A dictionary containing the parsed log entry's timestamp, content, and level.

        Raises:
            Exception: If parsing of the log line fails.
        """

        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        timestamp_match = re.search(timestamp_pattern, line)

        return {
            "timestamp": timestamp_match.group(0) if timestamp_match else None,
            "content": line.strip(),
            "level": LogService._detect_log_level(line),
        }

    @staticmethod
    def _detect_log_level(line: str) -> str:
        """
        Detects the log level of a given log line.

        Args:
            line (str): A single line of the log data.

        Returns:
            str: The log level of the given log line, which can be "ERROR", "WARNING", "INFO", or "UNKNOWN".
        """

        line = line.upper()
        if "ERROR" in line:
            return "ERROR"
        elif "WARNING" in line:
            return "WARNING"
        elif "INFO" in line:
            return "INFO"
        return "UNKNOWN"

    @staticmethod
    def _extract_line_number(error_text: str) -> Optional[int]:
        """
        Extracts the line number from the given error text, if available.

        Args:
            error_text (str): The error text to parse.

        Returns:
            Optional[int]: The line number where the error occurred, if found. Otherwise, None.
        """
        line_match = re.search(r"line (\d+)", error_text)
        return int(line_match.group(1)) if line_match else None

    @staticmethod
    def _generate_suggestion(error_type: str, error_text: str) -> str:
        """
        Generates a suggestion for fixing the given error based on the error type and text.

        Args:
            error_type (str): The type of error.
            error_text (str): The error text.

        Returns:
            str: A suggestion for fixing the given error.
        """

        if "ImportError" in error_text:
            return "Check if the required package is installed and accessible"
        elif "SyntaxError" in error_text:
            return "Review the code syntax at the indicated line"
        elif "TypeError" in error_text:
            return "Verify the data types of the variables being used"
        return "Review the error message and surrounding code context"

    @staticmethod
    def _create_timeline(parsed_logs: List[Dict]) -> List[Dict]:
        """
        Creates a timeline of log events, sorted by timestamp.

        Args:
            parsed_logs (List[Dict]): A list of dictionaries containing log information.

        Returns:
            List[Dict]: A list of dictionaries containing the log event, its timestamp, and level.
        """

        timeline = []
        for log in parsed_logs:
            if log["timestamp"]:
                timeline.append(
                    {
                        "time": log["timestamp"],
                        "event": log["content"],
                        "level": log["level"],
                    }
                )
        return sorted(timeline, key=lambda x: x["time"])

    @staticmethod
    def _create_summary(parsed_logs: List[Dict]) -> Dict:
        """
        Creates a summary of log events, including total logs, level distribution, and error rate.

        Args:
            parsed_logs (List[Dict]): A list of dictionaries containing log information.

        Returns:
            Dict: A dictionary containing the summary of log events.
        """
        
        levels = {"ERROR": 0, "WARNING": 0, "INFO": 0, "UNKNOWN": 0}
        for log in parsed_logs:
            levels[log["level"]] += 1

        return {
            "total_logs": len(parsed_logs),
            "level_distribution": levels,
            "error_rate": levels["ERROR"] / len(parsed_logs) if parsed_logs else 0,
        }
