warning: in the working copy of 'app.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/app.py b/app.py[m
[1mindex 13bbbf2..eec3a50 100644[m
[1m--- a/app.py[m
[1m+++ b/app.py[m
[36m@@ -16,7 +16,6 @@[m [mfrom flask_limiter import Limiter[m
 from flask_limiter.util import get_remote_address[m
 # Security imports[m
 from flask_talisman import Talisman[m
[31m-from flask_cors import CORS[m
 import jwt[m
 import bcrypt[m
 import re[m
[36m@@ -66,8 +65,13 @@[m [mdef create_app(config_name=None):[m
     force_https = app.config.get('ENV', 'production') == 'production'[m
     Talisman(app, content_security_policy=csp, force_https=force_https)[m
     [m
[31m-    # Configure CORS to restrict access to trusted domains[m
[31m-    CORS(app, resources={r"/*": {"origins": ["http://localhost:*", "https://*.solar-assistant.example.com"]}})[m
[32m+[m[32m    # Manually add CORS headers instead of using flask_cors[m
[32m+[m[32m    @app.after_request[m
[32m+[m[32m    def add_cors_headers(response):[m
[32m+[m[32m        response.headers['Access-Control-Allow-Origin'] = '*'[m
[32m+[m[32m        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'[m
[32m+[m[32m        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'[m
[32m+[m[32m        return response[m
     [m
     # Set up rate limiting[m
     limiter = Limiter([m
[1mdiff --git a/forms.py b/forms.py[m
[1mindex d7920f1..a40859d 100644[m
[1m--- a/forms.py[m
[1m+++ b/forms.py[m
[36m@@ -1,7 +1,6 @@[m
 from flask_wtf import FlaskForm[m
 from wtforms import StringField, SubmitField, TextAreaField[m
 from wtforms.validators import DataRequired, Length[m
[31m-from markupsafe import Markup[m
 [m
 class PromptForm(FlaskForm):[m
     """Form for solar assistant prompts with validation"""[m
[1mdiff --git a/solar_design_agent.py b/solar_design_agent.py[m
[1mindex 3e2b1a8..e69de29 100644[m
[1m--- a/solar_design_agent.py[m
[1m+++ b/solar_design_agent.py[m
[36m@@ -1,153 +0,0 @@[m
[31m-import openai[m
[31m-import os[m
[31m-import logging[m
[31m-from logging.handlers import RotatingFileHandler[m
[31m-[m
[31m-# Initialize logging[m
[31m-def setup_logging():[m
[31m-    if not os.path.exists('logs'):[m
[31m-        os.mkdir('logs')[m
[31m-    file_handler = RotatingFileHandler('logs/solar_assistant.log', maxBytes=10240, backupCount=5)[m
[31m-    file_handler.setFormatter(logging.Formatter([m
[31m-        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'[m
[31m-    ))[m
[31m-    file_handler.setLevel(logging.INFO)[m
[31m-    [m
[31m-    agent_logger = logging.getLogger('solar_design_agent')[m
[31m-    agent_logger.setLevel(logging.INFO)[m
[31m-    agent_logger.addHandler(file_handler)[m
[31m-    [m
[31m-    return agent_logger[m
[31m-[m
[31m-logger = setup_logging()[m
[31m-[m
[31m-class SolarDesignAgent:[m
[31m-    """[m
[31m-    Core functionality for the Solar Design Assistant.[m
[31m-    This class handles interactions with the OpenAI API to generate[m
[31m-    solar system design recommendations and reports.[m
[31m-    """[m
[31m-    def __init__(self, api_key, model="gpt-4"):[m
[31m-        """[m
[31m-        Initialize the Solar Design Agent.[m
[31m-        [m
[31m-        Args:[m
[31m-            api_key: OpenAI API key[m
[31m-            model: OpenAI model to use[m
[31m-        """[m
[31m-        self.model = model[m
[31m-        try:[m
[31m-            if not api_key:[m
[31m-                logger.error("OpenAI API key is missing")[m
[31m-                raise ValueError("OpenAI API key is required")[m
[31m-                [m
[31m-            key_prefix = api_key[:4] if len(api_key) > 4 else ""[m
[31m-            key_suffix = api_key[-4:] if len(api_key) > 4 else ""[m
[31m-            logger.info(f"Setting OpenAI API key: {key_prefix}...{key_suffix}")[m
[31m-            [m
[31m-            openai.api_key = api_key[m
[31m-            self.client = openai  # use module-level API[m
[31m-            logger.info("OpenAI client initialized successfully")[m
[31m-        except Exception as e:[m
[31m-            logger.error(f"Error initializing OpenAI client: {e}")[m
[31m-            import traceback[m
[31m-            logger.error(traceback.format_exc())[m
[31m-            self.client = None[m
[31m-    [m
[31m-    def load_system_prompt(self, prompt_path):[m
[31m-        """[m
[31m-        Load the system prompt from a file.[m
[31m-        [m
[31m-        Args:[m
[31m-            prompt_path: Path to the prompt file[m
[31m-            [m
[31m-        Returns:[m
[31m-            str: The system prompt[m
[31m-        """[m
[31m-        try:[m
[31m-            with open(prompt_path, "r", encoding="utf-8") as f:[m
[31m-                system_prompt = f.read()[m
[31m-                logger.info(f"Successfully loaded prompt from {prompt_path}")[m
[31m-                return system_prompt[m
[31m-        except FileNotFoundError:[m
[31m-            default_prompt = "You are a helpful solar PV system design assistant."[m
[31m-            logger.error(f"Prompt file not found: {prompt_path}")[m
[31m-            return default_prompt[m
[31m-    [m
[31m-    def load_template(self, template_path):[m
[31m-        """[m
[31m-        Load the report template from a file.[m
[31m-        [m
[31m-        Args:[m
[31m-            template_path: Path to the template file[m
[31m-            [m
[31m-        Returns:[m
[31m-            str: The report template[m
[31m-        """[m
[31m-        try:[m
[31m-            with open(template_path, "r", encoding="utf-8") as tf:[m
[31m-                template_content = tf.read()[m
[31m-                logger.info(f"Loaded ProReport template from {template_path}")[m
[31m-                return template_content[m
[31m-        except FileNotFoundError:[m
[31m-            logger.error(f"Template file not found: {template_path}")[m
[31m-            return ""[m
[31m-    [m
[31m-    def generate_response(self, user_prompt, system_prompt, template=None):[m
[31m-        """[m
[31m-        Generate a response using the OpenAI API.[m
[31m-        [m
[31m-        Args:[m
[31m-            user_prompt: User's input[m
[31m-            system_prompt: System prompt to guide the AI[m
[31m-            template: Optional template for formatting[m
[31m-            [m
[31m-        Returns:[m
[31m-            str: The generated response[m
[31m-        """[m
[31m-        if self.client is None:[m
[31m-            logger.error("OpenAI client is not initialized")[m
[31m-            return "Error: OpenAI service is unavailable"[m
[31m-        [m
[31m-        full_system_prompt = system_prompt[m
[31m-        if template:[m
[31m-            full_system_prompt += "\n" + template[m
[31m-        [m
[31m-        try:[m
[31m-            logger.info(f"Processing prompt of length {len(user_prompt)}")[m
[31m-            [m
[31m-            response = self.client.ChatCompletion.create([m
[31m-                model=self.model,[m
[31m-                messages=[[m
[31m-                    {"role": "system", "content": full_system_prompt},[m
[31m-                    {"role": "user", "content": user_prompt}[m
[31m-                ][m
[31m-            )[m
[31m-            [m
[31m-            response_text = response.choices[0].message.content[m
[31m-            logger.info(f"Successfully generated response of length {len(response_text)}")[m
[31m-            [m
[31m-            return response_text[m
[31m-        except Exception as e:[m
[31m-            logger.error(f"OpenAI API Error: {e}")[m
[31m-            return f"Error generating response: {e}"[m
[31m-[m
[31m-# Example usage[m
[31m-if __name__ == "__main__":[m
[31m-    # This code runs when the script is executed directly[m
[31m-    from dotenv import load_dotenv[m
[31m-    load_dotenv()[m
[31m-    [m
[31m-    api_key = os.getenv("OPENAI_API_KEY")[m
[31m-    agent = SolarDesignAgent(api_key)[m
[31m-    [m
[31m-    prompt_path = os.path.join("prompts", "kbs_solar_prompt_final.txt")[m
[31m-    template_path = os.path.join("prompts", "proreport_template.md")[m
[31m-    [m
[31m-    system_prompt = agent.load_system_prompt(prompt_path)[m
[31m-    template = agent.load_template(template_path)[m
[31m-    [m
[31m-    user_prompt = "Can you explain how solar panels work?"[m
[31m-    response = agent.generate_response(user_prompt, system_prompt, template)[m
[31m-    [m
[31m-    print(response)[m
\ No newline at end of file[m
[1mdiff --git a/web_app.py b/web_app.py[m
[1mindex 1115d8e..f90b88b 100644[m
[1m--- a/web_app.py[m
[1m+++ b/web_app.py[m
[36m@@ -1,270 +1,18 @@[m
[31m-from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify[m
[31m-import os[m
[31m-import logging[m
[31m-import sys[m
[31m-import threading[m
[31m-import subprocess[m
[31m-from io import BytesIO[m
[31m-from docx import Document[m
[31m-from dotenv import load_dotenv[m
[31m-from flask_limiter import Limiter[m
[31m-from flask_limiter.util import get_remote_address[m
[31m-from flask_talisman import Talisman[m
[31m-from flask_cors import CORS[m
[31m-import re[m
[31m-from forms import PromptForm[m
[31m-from solar_design_agent import SolarDesignAgent, setup_logging[m
[32m+[m[32mfrom flask import Flask, request, jsonify[m
 [m
[31m-# Initialize logging[m
[31m-logger = setup_logging()[m
[32m+[m[32mapp = Flask(__name__)[m
 [m
[31m-def create_app(config_name=None):[m
[31m-    # Load environment variables[m
[31m-    load_dotenv()[m
[31m-    [m
[31m-    # Create and configure the app[m
[31m-    app = Flask(__name__)[m
[31m-    [m
[31m-    # Configure secret key from environment or generate a random one[m
[31m-    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', os.urandom(24).hex())[m
[31m-    app.config['DEBUG'] = os.getenv('FLASK_ENV', 'production') != 'production'[m
[31m-    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')[m
[31m-    app.config['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'gpt-4')[m
[31m-    app.config['PROMPT_PATH'] = os.getenv('PROMPT_PATH', 'prompts/kbs_solar_prompt_final.txt')[m
[31m-    app.config['TEMPLATE_PATH'] = os.getenv('TEMPLATE_PATH', 'prompts/proreport_template.md')[m
[31m-    [m
[31m-    # Security enhancements[m
[31m-    # Set up Flask-Talisman for security headers (CSP, HSTS, etc.)[m
[31m-    csp = {[m
[31m-        'default-src': "'self'",[m
[31m-        'style-src': ["'self'", "'unsafe-inline'"],  # Allow inline styles for simplicity[m
[31m-        'script-src': ["'self'"],[m
[31m-        'img-src': ["'self'", "data:"],[m
[31m-        'font-src': ["'self'"],[m
[31m-        'connect-src': ["'self'", "mailto:", "https://www.linkedin.com", "https://www.facebook.com", [m
[31m-                        "https://api.whatsapp.com", "https://docs.google.com"],[m
[31m-        'form-action': ["'self'", "mailto:", "https://www.linkedin.com", "https://www.facebook.com", [m
[31m-                        "https://api.whatsapp.com", "https://docs.google.com"][m
[31m-    }[m
[31m-    [m
[31m-    # Only enable HTTPS in production[m
[31m-    force_https = app.config.get('ENV', 'production') == 'production'[m
[31m-    Talisman(app, content_security_policy=csp, force_https=force_https)[m
[31m-    [m
[31m-    # Configure CORS to restrict access to trusted domains[m
[31m-    CORS(app, resources={r"/*": {"origins": ["http://localhost:*", "https://*.solar-assistant.example.com"]}})[m
[31m-    [m
[31m-    # Set up rate limiting[m
[31m-    limiter = Limiter([m
[31m-        app=app,[m
[31m-        key_func=get_remote_address,[m
[31m-        default_limits=["200 per day", "50 per hour"],[m
[31m-        storage_uri="memory://",[m
[31m-    )[m
[31m-    [m
[31m-    # Initialize the Solar Design Agent[m
[31m-    try:[m
[31m-        api_key = app.config.get('OPENAI_API_KEY')[m
[31m-        solar_agent = SolarDesignAgent(api_key, model=app.config.get('OPENAI_MODEL'))[m
[31m-        logger.info("Solar Design Agent initialized successfully")[m
[31m-    except Exception as e:[m
[31m-        logger.error(f"Error initializing Solar Design Agent: {e}")[m
[31m-        import traceback; logger.error(traceback.format_exc())[m
[31m-        solar_agent = None  # Handle None in routes[m
[31m-    [m
[31m-    # Add security middleware[m
[31m-    @app.before_request[m
[31m-    def security_checks():[m
[31m-        # Validate request data to prevent injection attacks[m
[31m-        if request.method == 'POST':[m
[31m-            # Check for suspicious patterns in form data[m
[31m-            for key, value in request.form.items():[m
[31m-                if isinstance(value, str) and contains_suspicious_patterns(value):[m
[31m-                    logger.warning(f"Potentially malicious input detected from {request.remote_addr}")[m
[31m-                    return render_template('error.html', error="Invalid input detected"), 400[m
[31m-        [m
[31m-        # Prevent clickjacking by checking Referer[m
[31m-        if request.method != 'GET' and not is_safe_referrer(request.referrer):[m
[31m-            logger.warning(f"Potential CSRF attempt from {request.remote_addr} with referrer {request.referrer}")[m
[31m-            return render_template('error.html', error="Invalid request origin"), 403[m
[31m-    [m
[31m-    # Add health check endpoints[m
[31m-    @app.route('/health')[m
[31m-    @limiter.exempt  # Don't rate limit health checks[m
[31m-    def health_check():[m
[31m-        return jsonify({"status": "healthy", "version": "1.0.0"})[m
[31m-    [m
[31m-    @app.route("/healthz")[m
[31m-    @limiter.exempt  # Don't rate limit health checks[m
[31m-    def healthz():[m
[31m-        """Health check endpoint for Render monitoring."""[m
[31m-        return jsonify({"status": "healthy"}), 200[m
[32m+[m[32m# Manual CORS headers since flask_cors import may break compatibility[m
[32m+[m[32m@app.after_request[m
[32m+[m[32mdef add_cors_headers(response):[m
[32m+[m[32m    response.headers['Access-Control-Allow-Origin'] = '*'[m
[32m+[m[32m    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'[m
[32m+[m[32m    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'[m
[32m+[m[32m    return response[m
 [m
[31m-    # Error handlers[m
[31m-    @app.errorhandler(404)[m
[31m-    def not_found_error(error):[m
[31m-        return render_template('error.html', error="Page not found"), 404[m
[31m-    [m
[31m-    @app.errorhandler(500)[m
[31m-    def internal_error(error):[m
[31m-        logger.error(f"Server Error: {error}")[m
[31m-        return render_template('error.html', error="An internal error occurred"), 500[m
[31m-    [m
[31m-    @app.errorhandler(429)[m
[31m-    def ratelimit_handler(e):[m
[31m-        logger.warning(f"Rate limit exceeded: {e.description}")[m
[31m-        return render_template('error.html', error=f"Rate limit exceeded. {e.description}"), 429[m
[31m-    [m
[31m-    @app.errorhandler(Exception)[m
[31m-    def unhandled_exception(e):[m
[31m-        logger.error(f"Unhandled Exception: {e}")[m
[31m-        if app.config['DEBUG']:[m
[31m-            # In debug mode, let the default handler deal with it[m
[31m-            raise e[m
[31m-        return render_template('error.html', error="An unexpected error occurred"), 500[m
[31m-    [m
[31m-    # Routes[m
[31m-    @app.route('/', methods=['GET', 'POST'])[m
[31m-    def index():[m
[31m-        form = PromptForm()[m
[31m-        response_text = ""[m
[31m-        error_message = None[m
[31m-        [m
[31m-        # Check if Solar Design Agent is properly initialized[m
[31m-        if solar_agent is None:[m
[31m-            error_message = "OpenAI service is currently unavailable. Please try again later."[m
[31m-            logger.error("Route accessed with uninitialized Solar Design Agent")[m
[31m-            return render_template('index.html', [m
[31m-                                 form=form,[m
[31m-                                 response=session.get('response_text', ''), [m
[31m-                                 error=error_message)[m
[31m-        [m
[31m-        # Load system prompt and template[m
[31m-        system_prompt = solar_agent.load_system_prompt(app.config['PROMPT_PATH'])[m
[31m-        template = solar_agent.load_template(app.config['TEMPLATE_PATH'])[m
[31m-        [m
[31m-        if form.validate_on_submit():[m
[31m-            # Input validation is handled by WTForms[m
[31m-            prompt = form.prompt.data[m
[31m-            [m
[31m-            # Generate response using the Solar Design Agent[m
[31m-            response_text = solar_agent.generate_response(prompt, system_prompt, template)[m
[31m-            [m
[31m-            # Convert Markdown line breaks to HTML <br> tags for proper display[m
[31m-            # This preserves formatting in the HTML response[m
[31m-            formatted_response = response_text.replace('\n', '<br>')[m
[31m-            [m
[31m-            # Store both versions - original for download, formatted for display[m
[31m-            session['response_text'] = response_text[m
[31m-            session['formatted_response'] = formatted_response[m
[31m-        [m
[31m-        # Use the formatted response for display if available[m
[31m-        display_response = session.get('formatted_response', session.get('response_text', ''))[m
[31m-        [m
[31m-        return render_template('index.html', [m
[31m-                              form=form,[m
[31m-                              response=display_response, [m
[31m-                              error=error_message)[m
[31m-    [m
[31m-    @app.route('/clear')[m
[31m-    def clear():[m
[31m-        session.pop('response_text', None)[m
[31m-        session.pop('formatted_response', None)[m
[31m-        return redirect(url_for('index'))[m
[31m-    [m
[31m-    @app.route('/view-report', methods=['GET', 'POST'])[m
[31m-    def view_report():[m
[31m-        # Allow editing and saving updated report text[m
[31m-        if request.method == 'POST':[m
[31m-            updated = request.form.get('report_text', '')[m
[31m-            session['response_text'] = updated[m
[31m-        raw_text = session.get('response_text', 'No report available.')[m
[31m-        # Construct shareable URL for social/sharing[m
[31m-        share_url = request.url[m
[31m-        return render_template('view_report.html', response=raw_text, share_url=share_url)[m
[31m-    [m
[31m-    @app.route('/download-report')[m
[31m-    def download_report():[m
[31m-        response_text = session.get('response_text', 'No report available.')[m
[31m-        [m
[31m-        if response_text == 'No report available.':[m
[31m-            logger.warning("Attempted to download an empty report")[m
[31m-            return redirect(url_for('index'))[m
[31m-            [m
[31m-        try:[m
[31m-            doc = Document()[m
[31m-            doc.add_heading("Solar System Design Report", 0)[m
[31m-            [m
[31m-            for line in response_text.split('\n'):[m
[31m-                if line.strip().startswith("**") and line.strip().endswith("**"):[m
[31m-                    doc.add_heading(line.strip().strip("*"), level=1)[m
[31m-                else:[m
[31m-                    doc.add_paragraph(line.strip())[m
[31m-            [m
[31m-            file_stream = BytesIO()[m
[31m-            doc.save(file_stream)[m
[31m-            file_stream.seek(0)[m
[31m-            [m
[31m-            logger.info("Report document generated successfully")[m
[31m-            [m
[31m-            return send_file([m
[31m-                file_stream,[m
[31m-                as_attachment=True,[m
[31m-                download_name="Solar_Report.docx",[m
[31m-                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'[m
[31m-            )[m
[31m-        except Exception as e:[m
[31m-            logger.error(f"Error generating report document: {e}")[m
[31m-            return render_template('error.html', error="Error generating document"), 500[m
[31m-    [m
[31m-    return app[m
[32m+[m[32m@app.route('/')[m
[32m+[m[32mdef home():[m
[32m+[m[32m    return jsonify({"message": "Welcome to the API"})[m
 [m
[31m-def contains_suspicious_patterns(value):[m
[31m-    """Check for potentially malicious patterns in input"""[m
[31m-    # Check for common SQL injection or XSS patterns[m
[31m-    suspicious_patterns = [[m
[31m-        r"(?i)(<script|javascript:|on\w+=|\balert\(|\beval\()",  # Basic XSS[m
[31m-        r"(?i)(union\s+select|insert\s+into|update\s+.*?\s+set|delete\s+from)",  # SQL injection[m
[31m-        r"(?i)(\.\.\/|\.\.\\|\/etc\/passwd)"  # Path traversal[m
[31m-    ][m
[31m-    [m
[31m-    return any(re.search(pattern, value) for pattern in suspicious_patterns)[m
[31m-[m
[31m-def is_safe_referrer(referrer):[m
[31m-    """Validate that request comes from an allowed origin"""[m
[31m-    if not referrer:[m
[31m-        return True  # No referrer might be OK depending on your security posture[m
[31m-    [m
[31m-    allowed_hosts = ['localhost', '127.0.0.1', 'solar-assistant.example.com'][m
[31m-    for host in allowed_hosts:[m
[31m-        if host in referrer:[m
[31m-            return True[m
[31m-    [m
[31m-    return False[m
[31m-[m
[31m-def check_for_updates():[m
[31m-    """Run the dependency update checker in a subprocess"""[m
[31m-    try:[m
[31m-        # Start the update process dialog[m
[31m-        print("\n" + "-" * 60)[m
[31m-        print("Checking for dependency updates...")[m
[31m-        print("-" * 60)[m
[31m-        [m
[31m-        # Execute the update script and pass its output to the terminal[m
[31m-        update_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update_dependencies.py")[m
[31m-        subprocess.run([sys.executable, update_script], check=False)[m
[31m-        [m
[31m-        print("-" * 60 + "\n")[m
[31m-    except Exception as e:[m
[31m-        print(f"Error checking for updates: {e}")[m
[31m-[m
[31m-# Application entry point[m
 if __name__ == '__main__':[m
[31m-    # Check for updates before starting the app[m
[31m-    update_thread = threading.Thread(target=check_for_updates)[m
[31m-    update_thread.daemon = True[m
[31m-    update_thread.start()[m
[31m-    [m
[31m-    app = create_app()[m
[31m-    port = int(os.getenv('PORT', 8003))[m
[31m-    app.run(debug=app.config['DEBUG'], port=port)[m
\ No newline at end of file[m
[32m+[m[32m    app.run(debug=True)[m
\ No newline at end of file[m
