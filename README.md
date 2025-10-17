# Automated Student App Builder System

A comprehensive Python application that automatically builds, deploys, and updates web applications using LLM assistance through aipipe.org API and GitHub integration.

## 🚀 Features

- **FastAPI Server**: High-performance RESTful API with automatic documentation
- **LLM Integration**: Uses aipipe.org API for intelligent code generation
- **GitHub Integration**: Automatic repository creation, file management, and Pages deployment
- **Attachment Handling**: Processes base64 data URIs and file attachments
- **Round-based Updates**: Supports both initial builds (Round 1) and revisions (Round 2)
- **Robust Error Handling**: Exponential backoff retry logic and comprehensive logging
- **Security**: Secret verification and safe file handling

## 📋 Requirements

- Python 3.8+
- GitHub Personal Access Token
- aipipe.org API Token
- Student Secret (shared with instructors)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd app-builder-deployer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   AIPIPE_TOKEN=your_aipipe_token_here
   STUDENT_SECRET=your_student_secret_here
   GITHUB_TOKEN=your_github_personal_access_token_here
   GITHUB_USERNAME=your_github_username
   DEBUG=True
   PORT=8000
   LOG_LEVEL=INFO
   ```

## 🚀 Usage

### Starting the Server

```bash
# Option 1: Direct execution
python app.py

# Option 2: Using the startup script
python run_server.py

# Option 3: Using uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000` (or the port specified in `.env`).

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints

#### POST `/api-endpoint`

Main endpoint for receiving app build requests.

**Request Format**:
```json
{
  "email": "student@example.com",
  "secret": "your_student_secret",
  "task": "captcha-solver-abc123",
  "round": 1,
  "nonce": "ab12-cd34-ef56",
  "brief": "Create a captcha solver that handles ?url=https://.../image.png",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "Page displays captcha URL passed at ?url=...",
    "Page displays solved captcha text within 15 seconds"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

**Response**:
```json
{
  "status": "accepted",
  "message": "Request accepted and processing started",
  "task": "captcha-solver-abc123",
  "round": 1,
  "timestamp": "2024-01-01T12:00:00"
}
```

#### GET `/health`

Health check endpoint.

#### GET `/status/<nonce>`

Get status of a specific request by nonce.

## 🏗️ Architecture

### Project Structure

```
app-builder-deployer/
├── app.py                 # FastAPI server
├── builder.py             # Main builder script
├── run_server.py          # Server startup script
├── example_request.json   # Example request payload
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── utils/                # Utility modules
    ├── __init__.py
    ├── aipipe_utils.py   # AIPipe API integration
    ├── github_utils.py   # GitHub API integration
    └── attachment_utils.py # File attachment processing
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AIPIPE_TOKEN` | AIPipe API token | Yes |
| `STUDENT_SECRET` | Secret shared with instructors | Yes |
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `GITHUB_USERNAME` | GitHub username | Yes |
| `DEBUG` | Enable debug mode | No |
| `PORT` | Server port (default: 8000) | No |

### GitHub Token Permissions

Your GitHub Personal Access Token needs the following permissions:
- `repo` (Full control of private repositories)
- `public_repo` (Access to public repositories)
- `workflow` (Update GitHub Action workflows)

## 📝 Logging

The application creates detailed logs in:
- `app_builder.log`: API server logs
- `builder.log`: Builder script logs

Log levels can be configured via the `LOG_LEVEL` environment variable.

## 🔒 Security

- **Secret Verification**: All requests are validated against the configured student secret
- **Safe File Handling**: Attachments are processed safely with proper validation
- **No Secrets in Git**: The system avoids committing sensitive information
- **Input Validation**: All inputs are validated before processing

## 🚨 Error Handling

The system includes comprehensive error handling:

- **Exponential Backoff**: Retry failed operations with increasing delays
- **Input Validation**: Validates all incoming data
- **Safe Execution**: Graceful handling of unexpected errors
- **Detailed Logging**: Comprehensive error logging for debugging

## 🔄 Round-based Processing

### Round 1 (Initial Build)
- Creates new GitHub repository
- Generates complete web application
- Deploys to GitHub Pages
- Notifies evaluation endpoint

### Round 2 (Revision)
- Uses existing repository
- Modifies existing code based on new brief
- Updates repository with changes
- Notifies evaluation endpoint

## 📊 Monitoring

### Health Checks
- `/health` endpoint for basic health monitoring
- `/status/<nonce>` for request-specific status

### Logs
- Structured logging with timestamps
- Error tracking and debugging information
- Performance metrics

## 🛠️ Development

### Running in Development Mode

```bash
export DEBUG=True
export PORT=8000
python app.py
```

### Testing

```bash
# Test the API endpoint
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "your_secret",
    "task": "test-task",
    "round": 1,
    "nonce": "test-nonce",
    "brief": "Create a simple hello world app",
    "checks": ["Page displays hello world"],
    "evaluation_url": "https://httpbin.org/post"
  }'

# Test the API endpoints
curl http://localhost:8000/health

# Test app building (using example request)
python builder.py example_request.json
```

## 🚀 Render Deployment

This FastAPI application can be deployed on Render as a web service.

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Build Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 10000`
   - **Python Version**: 3.9 or higher

4. **Set Environment Variables**
   In Render dashboard, go to Environment tab and add:
   ```
   AIPIPE_TOKEN=your_aipipe_token_here
   STUDENT_SECRET=your_student_secret_here
   GITHUB_TOKEN=your_github_token_here
   GITHUB_USERNAME=your_github_username_here
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Your app will be available at `https://your-app-name.onrender.com`

### Verification
- Root endpoint: `https://your-app-name.onrender.com/` should return `{"status": "ok", "deployed": true}`
- Health check: `https://your-app-name.onrender.com/health`
- API docs: `https://your-app-name.onrender.com/docs`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the logs for error details
2. Verify environment variables are set correctly
3. Ensure GitHub token has proper permissions
4. Check aipipe.org API token validity
