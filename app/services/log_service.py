import re
from typing import List, Dict
from app.models.schemas import ErrorDetail
from datetime import datetime
from typing import Optional


class LogService:
    ERROR_PATTERNS = {
        "python": r"Traceback \(most recent call last\):[\s\S]+?\n\w+Error: .+",
        "javascript": r"(?:TypeError|ReferenceError|SyntaxError):.+",
        "api": r"(?:4\d{2}|5\d{2}) (?:Error|NOT_FOUND|BAD_REQUEST):.+",
    }

    @staticmethod
    def parse_logs(logs: str) -> List[Dict]:
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
        # Basic log line parser - extend based on your log format
        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        timestamp_match = re.search(timestamp_pattern, line)

        return {
            "timestamp": timestamp_match.group(0) if timestamp_match else None,
            "content": line.strip(),
            "level": LogService._detect_log_level(line),
        }

    @staticmethod
    def _detect_log_level(line: str) -> str:
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
        line_match = re.search(r"line (\d+)", error_text)
        return int(line_match.group(1)) if line_match else None

    @staticmethod
    def _generate_suggestion(error_type: str, error_text: str) -> str:
        # Basic suggestion generation - expand based on common errors
        if "ImportError" in error_text:
            return "Check if the required package is installed and accessible"
        elif "SyntaxError" in error_text:
            return "Review the code syntax at the indicated line"
        elif "TypeError" in error_text:
            return "Verify the data types of the variables being used"
        return "Review the error message and surrounding code context"

    @staticmethod
    def _create_timeline(parsed_logs: List[Dict]) -> List[Dict]:
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
        levels = {"ERROR": 0, "WARNING": 0, "INFO": 0, "UNKNOWN": 0}
        for log in parsed_logs:
            levels[log["level"]] += 1

        return {
            "total_logs": len(parsed_logs),
            "level_distribution": levels,
            "error_rate": levels["ERROR"] / len(parsed_logs) if parsed_logs else 0,
        }
