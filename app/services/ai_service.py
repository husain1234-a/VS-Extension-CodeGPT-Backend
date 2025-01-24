import google.generativeai as genai
from app.core.config import settings
from app.models.schemas import AIResponse


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    async def analyze_code(self, code: str, context: str = None) -> AIResponse:
        prompt = self._build_code_analysis_prompt(code, context)
        response = await self.model.generate_content_async(prompt)
        return self._parse_ai_response(response)

    async def analyze_logs(
        self, logs: str | list, context: str | list | dict = None
    ) -> AIResponse:
        if isinstance(logs, list):
            logs = "\n".join(logs)

        if isinstance(context, (dict, list)):
            context = ", ".join(
                [f"{k}: {v}" for k, v in context.items()]
                if isinstance(context, dict)
                else [str(item) for item in context]
            )

        prompt = self._build_log_analysis_prompt(logs, context)
        response = await self.model.generate_content_async(prompt)
        return self._parse_ai_response(response)

    def _build_code_analysis_prompt(self, code: str, context: str = None) -> str:
        return f"""
        You are an expert code analyzer focusing on API debugging and optimization.
        Analyze the following code:
        ```
        {code}
        ```
        {"Context: " + context if context else ""}
        
        Please provide:
            1. Code structure insights
            2. Potential improvements
            3. Best practices recommendations
            4. Specific code quality suggestions
        """

    def _build_log_analysis_prompt(self, logs: str, context: str = None) -> str:
        return f"""
        You are an expert in debugging API logs and identifying issues.
        Analyze the following logs:
        ```
        {logs}
        ```
        {"Context: " + context if context else ""}
        
        Please provide:
            1. Potential root causes
            2. Specific debugging steps
            3. Recommended fixes
            4. Best practices to prevent similar issues
        """

    def _parse_ai_response(self, response) -> AIResponse:
        content = response.text
        return AIResponse(
            content=content,
            suggestions=self._extract_suggestions(content),
            code_snippets=self._extract_code_snippets(content),
        )

    def _extract_suggestions(self, content: str) -> list:
        """
        Extracts suggestions from the AI response content.
        Looks for numbered/bulleted items and lines containing keywords like 'suggest', 'recommend', 'consider'.
        """
        suggestions = []
        lines = content.split("\n")

        suggestion_keywords = [
            "suggest",
            "recommend",
            "consider",
            "could",
            "should",
            "try",
        ]

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() and len(line) > 2 and line[1] == ".":
                suggestions.append(line[2:].strip())
                continue

            if line.startswith(("•", "-", "*")):
                suggestions.append(line[1:].strip())
                continue

            if any(keyword in line.lower() for keyword in suggestion_keywords):
                suggestions.append(line)

        return suggestions

    def _extract_code_snippets(self, content: str) -> list:
        """
        Extracts code snippets from the AI response content.
        Returns a list of dictionaries containing code and its language.
        """
        snippets = []
        lines = content.split("\n")
        current_snippet = []
        current_language = None
        in_code_block = False

        for line in lines:
            if line.startswith("```"):
                if in_code_block:
                    if current_snippet:
                        snippets.append(
                            {
                                "code": "\n".join(current_snippet),
                                "language": current_language or "text",
                            }
                        )
                    current_snippet = []
                    current_language = None
                    in_code_block = False
                else:
                    in_code_block = True
                    language_spec = line[3:].strip()
                    if language_spec:
                        current_language = language_spec.lower()
                continue

            if in_code_block:
                current_snippet.append(line)

        if current_snippet:
            snippets.append(
                {
                    "code": "\n".join(current_snippet),
                    "language": current_language or "text",
                }
            )

        return snippets
