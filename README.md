# BuiltByRays™ CFO OS

A comprehensive Financial Operating System with AI-powered chatbot assistance for business financial management.

## 🚀 **ONE-CLICK STARTUP** (NEW!)

### **For Windows Users:**
1. **Double-click** `START_CFO_OS.bat`
2. **That's it!** Everything starts automatically

### **For Unix/Linux Users:**
1. **Run** `./START_CFO_OS.sh`
2. **That's it!** Everything starts automatically

### **What Happens Automatically:**
- ✅ **Installs all dependencies** (Python & Node.js packages)
- ✅ **Creates configuration files** (.env template)
- ✅ **Starts the Python backend** (Flask server)
- ✅ **Starts the vault watcher** (file synchronization)
- ✅ **Starts the Electron desktop app** (if Node.js available)
- ✅ **Opens the web interface** in your browser
- ✅ **Shows status and instructions**

### **Only Manual Step Required:**
- Add your OpenAI API key to the `.env` file (one-time setup)

---

## 📋 Prerequisites

- **Python 3.8 or higher** (required)
- **Node.js 16 or higher** (optional, for desktop app)
- **OpenAI API key** (required for AI features)

## 🔧 Manual Installation (Alternative)

If you prefer manual installation:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BuiltByRays_CFO_OS
   ```

2. **Run the automated setup**
   ```bash
   python setup.py
   ```

3. **Configure your API key**
   - Edit the `.env` file
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

4. **Start the application**
   - **Windows**: Double-click `start_cfo_os.bat`
   - **Unix/Linux**: Run `./start_cfo_os.sh`
   - **Manual**: `python start_chatbot.py`

## 📁 Project Structure

```
BuiltByRays_CFO_OS/
├── START_CFO_OS.bat      # 🚀 ONE-CLICK STARTUP (Windows)
├── START_CFO_OS.sh       # 🚀 ONE-CLICK STARTUP (Unix/Linux)
├── auto_start.py         # 🤖 Automatic startup engine
├── rag-backend/          # Python Flask backend
│   ├── chatbot.py       # Main chatbot application
│   ├── embedder.py      # Vector store operations
│   ├── loader.py        # Document loading
│   └── requirements.txt # Python dependencies
├── electron-app/         # Electron desktop app
│   ├── main.js         # Main process
│   ├── index.html      # Main window
│   └── package.json    # Node.js dependencies
├── vault/               # Financial documents and data
├── setup.py            # Automated setup script
├── start_chatbot.py    # Python startup script
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables
The `.env` file is created automatically, but you need to add your API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Vault Structure
The `vault/` directory contains your financial documents organized by category:
- `00-Home/` - Welcome and navigation
- `01-Scope/` - Service scope and agreements
- `09-Financials/` - Financial data and analysis
- And more...

## 🎯 Features

### AI Chatbot
- **Context-aware responses** based on your vault documents
- **Financial expertise** with CFO-level knowledge
- **Real-time assistance** for financial decisions
- **Document search** across your entire vault

### Desktop Application
- **Electron-based** cross-platform desktop app
- **Integrated chat interface** with the AI backend
- **File synchronization** with your vault
- **Professional UI** for business use

### Web Interface
- **Flask-based** web server
- **RESTful API** for integration
- **Health monitoring** endpoints
- **CORS support** for cross-origin requests

## 🚀 Usage

### **Automatic Startup (Recommended)**
1. **Windows**: Double-click `START_CFO_OS.bat`
2. **Unix/Linux**: Run `./START_CFO_OS.sh`
3. **Add API key**: Edit `.env` file with your OpenAI key
4. **Access**: Web interface opens automatically at http://localhost:5000

### Manual Startup (Alternative)
1. **Web Interface**
   ```bash
   python start_chatbot.py
   ```
   Then open http://localhost:5000 in your browser

2. **Desktop App**
   ```bash
   cd electron-app
   npm start
   ```

3. **API Endpoints**
   - `GET /` - Application info
   - `POST /chat` - Chat with AI
   - `GET /health` - Health check
   - `POST /vault/query` - Direct vault queries
   - `POST /vault/update` - Update vault knowledge

### Chatbot Usage

The AI chatbot can help with:
- **Financial analysis** and reporting
- **Cash flow projections** and planning
- **Tax strategy** and compliance
- **Business development** and growth
- **Operational processes** and SOPs
- **HR and team management**
- **Technology infrastructure** decisions

## 🛠️ Development

### Adding New Features

1. **Backend (Python/Flask)**
   - Add new routes in `rag-backend/chatbot.py`
   - Extend the `CFOAIChatbot` class
   - Update requirements.txt for new dependencies

2. **Frontend (Electron)**
   - Modify `electron-app/index.html` for UI changes
   - Update `electron-app/main.js` for app logic
   - Add new dependencies to `electron-app/package.json`

3. **Vault Integration**
   - Add documents to appropriate `vault/` subdirectories
   - The system automatically indexes new `.md` and `.txt` files
   - Use the `/vault/update` endpoint to re-index

### Testing

```bash
# Run Python tests
python -m pytest tests/

# Test the API
curl http://localhost:5000/health

# Test the chatbot
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are our current financial goals?"}'
```

## 📦 Packaging

### Creating a Distribution

1. **Install all dependencies**
   ```bash
   npm run install:all
   ```

2. **Build the Electron app**
   ```bash
   npm run build
   ```

3. **Package for distribution**
   ```bash
   npm run package
   ```

### Distribution Files

The packaged application includes:
- **Python backend** with all dependencies
- **Electron desktop app** for Windows/macOS/Linux
- **Vault structure** with sample documents
- **Startup scripts** for easy deployment
- **Configuration templates** for quick setup

## 🔒 Security

### API Key Management
- Store your OpenAI API key in the `.env` file
- Never commit API keys to version control
- Use environment variables in production

### Data Privacy
- All vault documents are processed locally
- No financial data is sent to external services
- Vector embeddings are stored locally in ChromaDB

## 🆘 Troubleshooting

### Common Issues

1. **Python not found**
   - Install Python 3.8+ from python.org
   - Add Python to your system PATH

2. **Node.js not found**
   - Install Node.js 16+ from nodejs.org
   - Restart your terminal after installation

3. **OpenAI API errors**
   - Verify your API key in the `.env` file
   - Check your OpenAI account for usage limits

4. **Vault not loading**
   - Ensure the `vault/` directory exists
   - Check file permissions on vault documents
   - Verify document encoding (UTF-8)

5. **Port conflicts**
   - Change the port in `chatbot.py` if 5000 is in use
   - Update the frontend configuration accordingly

### Getting Help

- Check the logs in `rag-backend/chatbot_logs.json`
- Use the `/health` endpoint to diagnose issues
- Review the console output for error messages

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Support

For support and questions:
- Email: support@builtbyrays.com
- Documentation: https://docs.builtbyrays.com
- Issues: https://github.com/builtbyrays/cfo-os/issues

---

**BuiltByRays™ CFO OS** - Empowering businesses with intelligent financial management. 