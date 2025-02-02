import logging
from typing import Optional
from fastapi import HTTPException
import google.generativeai as genai
from app.core.config import settings
from app.models.ai_response import AIResponse


class AIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-pro")

    async def analyze_code(
        self, code: str, context: str = None, user_prompt: str = None
    ) -> AIResponse:
        try:
            prompt = self._build_code_analysis_prompt(code, context, user_prompt)
            response = await self.model.generate_content_async(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            self.logger.error(f"Error analyzing code: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def analyze_logs(
        self,
        logs: str | list,
        context: str | list | dict = None,
        user_prompt: str = None,
        code: str = None,
    ) -> AIResponse:
        try:
            if isinstance(logs, list):
                logs = "\n".join(logs)
            if isinstance(context, (dict, list)):
                context = ", ".join(
                    [f"{k}: {v}" for k, v in context.items()]
                    if isinstance(context, dict)
                    else [str(item) for item in context]
                )
            prompt = self._build_log_analysis_prompt(logs, context, user_prompt, code)
            response = await self.model.generate_content_async(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            self.logger.error(f"Error analyzing logs: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _build_code_analysis_prompt(
        self, code: str, context: str = None, user_prompt: str = None
    ) -> str:
        base_prompt = f"""
        You are an expert code analyzer focusing on API debugging and optimization.
        Analyze the following code:
        ```
        {code}
        ```
        {"Context: " + context if context else ""}
        
        Default Analysis Tasks:
        1. Code structure insights
        2. Potential improvements
        3. Best practices recommendations
        4. Specific code quality suggestions
        """
        if user_prompt:
            return f"""You are an expert consider this user prompt: {user_prompt}
            analyze the following code:
            ```
            {code}
            ```
            {"Context: " + context if context else ""}
            """
        return base_prompt.strip()

    def _build_log_analysis_prompt(
        self,
        logs: str,
        context: Optional[str] = None,
        user_prompt: Optional[str] = None,
        code: Optional[str] = None,
    ) -> str:
        """
        Build prompt for log analysis with caching for repeated requests.
        """
        if user_prompt:
            prompt = f"""You are an expert log analyzer. Consider this user prompt: {user_prompt}
            
            Analyze the following logs:
            ```
            {logs}
            ```
            """
            if code:
                prompt += f"\nRelated code:\n```\n{code}\n```"
            if context:
                prompt += f"\nContext: {context}"
            prompt += "based on code and logs give updated code"
            return prompt
        prompt = f"""
        You are an expert in debugging API logs and identifying issues.
        
        Analyze the following logs:
        ```
        {logs}
        ```
        
        Analysis Tasks:
        1. Potential root causes
        2. Specific debugging steps
        3. Recommended fixes
        4. Best practices to prevent similar issues
        5. Provide updated code to address the issue
        """.strip()
        if code:
            prompt += f"\n\nRelated code:\n```\n{code}\n```"
        if context:
            prompt += f"\n\nContext: {context}"
        return prompt

    def _parse_ai_response(self, response) -> AIResponse:
        content = response.text
        return AIResponse(
            content=content,
            suggestions=self._extract_suggestions(content),
            code_snippets=self._extract_code_snippets(content),
            chat_context=self._extract_chat_context(content),
        )

    def _extract_chat_context(self, content: str) -> str:
        """
        Extracts relevant context from the response that might be useful for future interactions.
        """
        key_points = []
        lines = content.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in [
                    "important",
                    "key",
                    "critical",
                    "note",
                    "recommendation",
                ]
            ):
                key_points.append(line.strip())
        return "\n".join(key_points) if key_points else None

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
