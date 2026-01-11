# 🛡️ AI Security Maturity Assessment Tool

A comprehensive security maturity assessment platform combining **NIST AI RMF** and **CSA AICM** frameworks with AI-powered auto-assessment capabilities.

## 🚀 Features

- **Multi-Framework Coverage**: NIST AI RMF (GOVERN, MAP, MEASURE, MANAGE) + 243 CSA AICM controls
- **AI Auto-Assessment**: Automated evidence analysis using OpenAI, Google Gemini, or Perplexity
- **Maturity Waves**: Progressive assessment in 3 phases (Foundation → Security → Operations)
- **Smart Scoring**: Business-friendly maturity levels (Not Implemented → Optimized)
- **Evidence Locker**: Upload policies, architecture diagrams, and documentation for AI analysis
- **Interactive Dashboard**: Real-time radar charts and maturity scoring

## 📦 Quick Start

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd maturity_ai_security

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

**Note**: This is a demo environment. Data is not persisted between sessions.

## 🔑 Configuration

### AI Provider Setup

The app supports three AI providers:

1. **OpenAI** (GPT-3.5/4)
   - Get API key: https://platform.openai.com/api-keys
   
2. **Google Gemini**
   - Get API key: https://makersuite.google.com/app/apikey
   
3. **Perplexity** (Sonar)
   - Get API key: https://www.perplexity.ai/settings/api

Configure your API key in the "Evidence Locker" tab.

## 📊 Usage

1. **Select Maturity Wave**: Choose Foundation, Security, or Operations phase
2. **Upload Evidence**: Add your security documentation to the Evidence Locker
3. **Auto-Assess**: Use AI to automatically evaluate controls based on your evidence
4. **Manual Review**: Adjust scores as needed using the maturity level selector
5. **Submit**: Save your assessment and view the dashboard
6. **Download**: Export your results before closing the session

## ⚠️ Demo Limitations

This MVP deployment has the following limitations:

- ❌ **No Persistent Storage**: Assessments are lost when the app restarts
- ❌ **No User Authentication**: Single-tenant demo mode
- ❌ **Ephemeral Evidence**: Uploaded documents are cleared on restart

**Recommendation**: Download your assessment results before closing the browser.

## 🏢 Enterprise Version

For production use with:
- ✅ Persistent database (PostgreSQL)
- ✅ Multi-user authentication
- ✅ Permanent evidence storage
- ✅ API access
- ✅ Custom integrations

Contact: [your-email@example.com]

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **NIST AI RMF**: National Institute of Standards and Technology
- **CSA AICM**: Cloud Security Alliance AI Controls Matrix
- Built with Streamlit, LangChain, and ChromaDB
