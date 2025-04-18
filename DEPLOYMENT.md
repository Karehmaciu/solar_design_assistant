# Solar Assistant Deployment Guide

This guide provides instructions for deploying the Solar Assistant application to various cloud platforms.

## Prerequisites

- Git installed on your local machine
- GitHub account (if using GitHub deployment methods)
- Cloud platform account (based on chosen deployment option)
- OpenAI API key

## Option 1: GitHub + Railway Deployment

[Railway](https://railway.app/) is a platform that makes deployment very simple with GitHub integration.

1. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com)
   - Click "New repository"
   - Name it `solar-assistant`
   - Choose "Private" for repository visibility
   - Initialize with README
   - Click "Create repository"

2. **Push Your Code to GitHub**:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/karemaciu/solar-assistant.git
   git push -u origin main
   ```

3. **Deploy to Railway**:
   - Go to [Railway](https://railway.app/)
   - Log in with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `solar-assistant` repository
   - Add environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `FLASK_SECRET`: A secure random string for session encryption
     - `PORT`: 8003
   - Click "Deploy"

## Option 2: Render

[Render](https://render.com/) offers a simple way to deploy web services with a generous free tier.

1. **Create a Render Account**:
   - Go to [Render](https://render.com/)
   - Sign up with your GitHub account

2. **Deploy Your Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Name: `solar-assistant`
   - Start Command: `gunicorn wsgi:flask_app`
   - Select Environment Variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `FLASK_SECRET`: A secure random string for session encryption
   - Click "Create Web Service"

## Option 3: Heroku

Heroku is a popular platform for Python applications.

1. **Install Heroku CLI**:

   ```bash
   # Download and install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**:

   ```bash
   heroku login
   heroku create solar-assistant-karemaciu
   ```

3. **Configure Environment Variables**:

   ```bash
   heroku config:set OPENAI_API_KEY=your_api_key
   heroku config:set FLASK_SECRET=your_secret_key
   ```

4. **Deploy Application**:

   ```bash
   git push heroku main
   ```

## Option 4: Google Cloud Run (Containerized)

For a more scalable solution, deploy to Google Cloud Run:

1. **Install Google Cloud SDK** from [here](https://cloud.google.com/sdk/docs/install)

2. **Initialize and Configure GCP**:

   ```bash
   gcloud init
   gcloud auth login
   gcloud projects create solar-assistant-app
   gcloud config set project solar-assistant-app
   ```

3. **Enable Required APIs**:

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

4. **Build and Deploy Container**:

   ```bash
   gcloud builds submit --tag gcr.io/solar-assistant-app/solar-assistant
   gcloud run deploy solar-assistant --image gcr.io/solar-assistant-app/solar-assistant --platform managed --allow-unauthenticated
   ```

5. **Set Environment Variables**:
   - Use the Google Cloud Console to set:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `FLASK_SECRET`: A secure random string

## Setting Up GitHub Repository with Required Permissions

To set up GitHub integration with Dependabot alerts and other permissions:

1. **Create a GitHub Repository** (if not done already)
2. Push your code to the repository
3. **Enable Dependabot Alerts**:
   - Go to repository settings
   - Navigate to "Security & analysis"
   - Enable "Dependabot alerts" and "Dependabot security updates"

4. **Set Up GitHub Actions** for CI/CD:
   - Create a `.github/workflows` directory
   - Add the workflow file below

## Monitoring and Analytics

Once deployed, consider adding:

1. **Uptime Monitoring**: Services like UptimeRobot or StatusCake
2. **Error Tracking**: Sentry.io integration
3. **Analytics**: Google Analytics or similar

## Security Considerations

1. **Always use environment variables** for secrets
2. Keep dependencies updated using the built-in `update_dependencies.py` script
3. Regularly review application logs for unusual activities
4. Consider implementing rate limiting per user if traffic increases

## Domain and SSL Configuration

For a professional appearance:

1. Purchase a domain (e.g., solarassistant.com)
2. Configure DNS records to point to your deployed application
3. Set up SSL certificates (most platforms handle this automatically)
