# Solar Assistant

An AI-powered solar system design assistant that helps users plan and size photovoltaic systems.

## Features

- Create detailed solar system designs based on user requirements
- Generate professional reports with system specifications
- Support for various battery types and solar configurations
- Dark mode interface for comfortable viewing
- Automatic dependency management

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/karemaciu/solar-assistant.git
   cd solar-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     FLASK_SECRET=your_secret_key_here
     ```

## Usage

Run the application:

```bash
python app.py
```

Access the web interface at http://localhost:8003

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Updating Dependencies

The application includes an automatic dependency checker/updater:

```bash
python update_dependencies.py
```

## License

Copyright © 2025 karemaciu. All rights reserved.
