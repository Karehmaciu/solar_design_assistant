"""Solar Design Agent for handling solar system design calculations and AI interactions."""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import json
import openai
from datetime import datetime
from pathlib import Path

class SolarDesignAgent:
    """Handles solar system design calculations and OpenAI interactions."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the Solar Design Agent.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use. Defaults to "gpt-4".
        """
        self.logger = logging.getLogger('solar_assistant')
        self._setup_openai_client(api_key)
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.template = self._load_report_template()

    def _setup_openai_client(self, api_key: Optional[str]) -> None:
        """Set up the OpenAI client with error handling.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        try:
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OpenAI API key is required")
            self.logger.info(f"Setting OpenAI API key: {key[:2]}...{key[-4:]}")
            
            try:
                # Try new-style client first (OpenAI v1.0.0+)
                self.client = openai.OpenAI(api_key=key)
                self.logger.info("OpenAI client initialized successfully")
            except (AttributeError, TypeError):
                # Fall back to old-style for older versions
                openai.api_key = key
                self.client = openai
                self.logger.info("OpenAI client initialized with legacy API")
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            raise

    def _load_system_prompt(self) -> str:
        """Load the system prompt from file."""
        try:
            prompt_path = "prompts/kbs_solar_prompt_final.txt"
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
                self.logger.info(f"Successfully loaded prompt from {prompt_path}")
                return prompt
        except FileNotFoundError:
            self.logger.warning("System prompt file not found, using default")
            return "You are a helpful solar PV system design assistant."
        except Exception as e:
            self.logger.error(f"Error loading system prompt: {e}")
            raise

    def _load_report_template(self) -> str:
        """Load the report template from file."""
        try:
            template_path = "prompts/proreport_template.md"
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
                self.logger.info(f"Loaded ProReport template from {template_path}")
                return template
        except FileNotFoundError:
            self.logger.warning("Report template file not found")
            return ""
        except Exception as e:
            self.logger.error(f"Error loading report template: {e}")
            raise

    def generate_system_design(self, 
                             prompt: str, 
                             language: str = "en",
                             max_retries: int = 3) -> Tuple[str, Optional[str]]:
        """Generate a solar system design based on the user's requirements.
        
        Args:
            prompt: User's design requirements
            language: Target language for the response
            max_retries: Maximum number of retries on API errors
        
        Returns:
            Tuple of (response text, error message if any)
        """
        if not prompt:
            return "", "Empty prompt provided"

        # Add language instruction to system prompt
        lang_map = {
            'en': 'English',
            'sw': 'Kiswahili',
            'ar': 'Arabic',
            'am': 'Amharic',
            'es': 'Spanish',
            'fr': 'French'
        }
        lang_name = lang_map.get(language, 'English')
        full_prompt = f"{self.system_prompt}\n{self.template}\nPlease respond in {lang_name}."
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": full_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content, None
            except openai.RateLimitError:
                error_msg = "Rate limit exceeded. Please try again in a moment."
                self.logger.warning(error_msg)
                return "", error_msg
            except openai.AuthenticationError:
                error_msg = "Authentication error. Please check your API key."
                self.logger.error(error_msg)
                return "", error_msg
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_msg = f"Error generating design after {max_retries} attempts: {str(e)}"
                    self.logger.error(error_msg)
                    return "", error_msg
                self.logger.warning(f"Attempt {retry_count} failed: {str(e)}")

    def validate_design(self, design_specs: Dict[str, Any]) -> List[str]:
        """Validate solar system design specifications.
        
        Args:
            design_specs: Dictionary containing design specifications
        
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        required_fields = [
            'daily_energy_demand',
            'system_voltage',
            'battery_capacity',
            'solar_array_size'
        ]
        
        for field in required_fields:
            if field not in design_specs:
                errors.append(f"Missing required field: {field}")
        
        # Validate numerical values
        if 'daily_energy_demand' in design_specs:
            try:
                demand = float(design_specs['daily_energy_demand'])
                if demand <= 0:
                    errors.append("Daily energy demand must be positive")
            except ValueError:
                errors.append("Invalid daily energy demand value")
        
        # Validate system voltage
        if 'system_voltage' in design_specs:
            valid_voltages = [12, 24, 48]
            try:
                voltage = int(design_specs['system_voltage'])
                if voltage not in valid_voltages:
                    errors.append(f"System voltage must be one of: {valid_voltages}")
            except ValueError:
                errors.append("Invalid system voltage value")
        
        return errors

    def save_design(self, design_data: Dict[str, Any], filepath: str) -> None:
        """Save the design data to a file.
        
        Args:
            design_data: Dictionary containing the design data
            filepath: Path to save the file
        """
        try:
            # Add timestamp and version info
            design_data['timestamp'] = datetime.now().isoformat()
            design_data['version'] = '1.0'
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(design_data, f, indent=2)
            
            self.logger.info(f"Design saved successfully to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving design: {e}")
            raise