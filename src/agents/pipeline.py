"""Translation pipeline implementation."""

import time
import os
from pathlib import Path
from typing import Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class TranslationPipeline:
    """Orchestrates the three-agent translation pipeline."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize translation pipeline.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = config.get("api", {}).get("model", "claude-3-5-sonnet-20241022")
        self.max_retries = config.get("api", {}).get("max_retries", 3)
        self.timeout = config.get("api", {}).get("timeout", 60)
        self.delay = config.get("api", {}).get("delay_between_requests", 1.0)

        # Load skill prompts
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict[str, str]:
        """Load skill prompts from markdown files."""
        skills = {}
        for agent_name, agent_config in self.config.get("agents", {}).items():
            skill_file = Path(agent_config["skill_file"])
            if skill_file.exists():
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skills[agent_name] = f.read()
        return skills

    def _call_agent(self, agent_name: str, input_text: str) -> str:
        """
        Call a single agent with retry logic.

        Args:
            agent_name: Name of the agent (agent1, agent2, agent3)
            input_text: Text to translate

        Returns:
            Translated text
        """
        skill_prompt = self.skills.get(agent_name, "")

        system_prompt = f"""{skill_prompt}

Please translate the following text according to the instructions above."""

        for attempt in range(self.max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": input_text
                        }
                    ]
                )

                translation = message.content[0].text.strip()
                time.sleep(self.delay)  # Rate limiting
                return translation

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Agent {agent_name} failed after {self.max_retries} attempts: {str(e)}")
                wait_time = 2 ** attempt
                print(f"Agent {agent_name} attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)

        return ""

    def process(self, english_input: str, test_id: int = 0) -> Dict[str, Any]:
        """
        Process text through the full translation pipeline.

        Args:
            english_input: Original English text (potentially with errors)
            test_id: Test case ID for logging

        Returns:
            Dictionary containing all translations and metadata
        """
        start_time = time.time()

        print(f"\nProcessing test case {test_id}...")
        print(f"Original (EN): {english_input[:100]}{'...' if len(english_input) > 100 else ''}")

        # Agent 1: EN → FR
        print("  Agent 1 (EN→FR)...")
        french = self._call_agent("agent1", english_input)
        print(f"  French: {french[:100]}{'...' if len(french) > 100 else ''}")

        # Agent 2: FR → HE
        print("  Agent 2 (FR→HE)...")
        hebrew = self._call_agent("agent2", french)
        print(f"  Hebrew: {hebrew[:100]}{'...' if len(hebrew) > 100 else ''}")

        # Agent 3: HE → EN
        print("  Agent 3 (HE→EN)...")
        final_english = self._call_agent("agent3", hebrew)
        print(f"  Final (EN): {final_english[:100]}{'...' if len(final_english) > 100 else ''}")

        duration = time.time() - start_time

        return {
            "test_id": test_id,
            "original": english_input,
            "french": french,
            "hebrew": hebrew,
            "final": final_english,
            "metadata": {
                "duration": duration,
                "success": True,
                "model": self.model
            }
        }

    def process_batch(self, test_cases: list) -> list:
        """
        Process multiple test cases.

        Args:
            test_cases: List of TestCase objects

        Returns:
            List of translation results
        """
        results = []
        total = len(test_cases)

        for idx, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"Processing {idx}/{total}")
            print(f"{'='*60}")

            try:
                result = self.process(test_case.corrupted, test_case.id)
                result["test_case"] = {
                    "id": test_case.id,
                    "original_clean": test_case.original,
                    "target_error_rate": test_case.target_error_rate,
                    "actual_error_rate": test_case.actual_error_rate,
                    "word_count": test_case.word_count
                }
                results.append(result)
            except Exception as e:
                print(f"Error processing test case {test_case.id}: {str(e)}")
                results.append({
                    "test_id": test_case.id,
                    "error": str(e),
                    "metadata": {"success": False}
                })

        return results
