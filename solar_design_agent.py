import openai
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize logging
def setup_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/solar_assistant.log', maxBytes=10240, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    agent_logger = logging.getLogger('solar_design_agent')
    agent_logger.setLevel(logging.INFO)
    agent_logger.addHandler(file_handler)
    
    return agent_logger

logger = setup_logging()

class SolarDesignAgent:
    """
    Core functionality for the Solar Design Assistant.
    This class handles interactions with the OpenAI API to generate
    solar system design recommendations and reports.
    """
    def __init__(self, api_key, model="gpt-4"):
        """
        Initialize the Solar Design Agent.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.model = model
        try:
            if not api_key:
                logger.error("OpenAI API key is missing")
                raise ValueError("OpenAI API key is required")
                
            key_prefix = api_key[:4] if len(api_key) > 4 else ""
            key_suffix = api_key[-4:] if len(api_key) > 4 else ""
            logger.info(f"Setting OpenAI API key: {key_prefix}...{key_suffix}")
            
            openai.api_key = api_key
            self.client = openai  # use module-level API
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.client = None
    
    def load_system_prompt(self, prompt_path):
        """
        Load the system prompt from a file.
        
        Args:
            prompt_path: Path to the prompt file
            
        Returns:
            str: The system prompt
        """
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
                logger.info(f"Successfully loaded prompt from {prompt_path}")
                return system_prompt
        except FileNotFoundError:
            default_prompt = "You are a helpful solar PV system design assistant."
            logger.error(f"Prompt file not found: {prompt_path}")
            return default_prompt
    
    def load_template(self, template_path):
        """
        Load the report template from a file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            str: The report template
        """
        try:
            with open(template_path, "r", encoding="utf-8") as tf:
                template_content = tf.read()
                logger.info(f"Loaded ProReport template from {template_path}")
                return template_content
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            return ""
    
    def generate_response(self, user_prompt, system_prompt, template=None):
        """
        Generate a response using the OpenAI API.
        
        Args:
            user_prompt: User's input
            system_prompt: System prompt to guide the AI
            template: Optional template for formatting
            
        Returns:
            str: The generated response
        """
        if self.client is None:
            logger.error("OpenAI client is not initialized")
            return "Error: OpenAI service is unavailable"
        
        full_system_prompt = system_prompt
        if template:
            full_system_prompt += "\n" + template
        
        try:
            logger.info(f"Processing prompt of length {len(user_prompt)}")
            
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"Successfully generated response of length {len(response_text)}")
            
            return response_text
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return f"Error generating response: {e}"

# Example usage
if __name__ == "__main__":
    # This code runs when the script is executed directly
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    agent = SolarDesignAgent(api_key)
    
    prompt_path = os.path.join("prompts", "kbs_solar_prompt_final.txt")
    template_path = os.path.join("prompts", "proreport_template.md")
    
    system_prompt = agent.load_system_prompt(prompt_path)
    template = agent.load_template(template_path)
    
    user_prompt = "Can you explain how solar panels work?"
    response = agent.generate_response(user_prompt, system_prompt, template)
    
    print(response)