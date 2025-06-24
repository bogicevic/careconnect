# CareConnect - Multi-Agent Healthcare System

CareConnect is an autonomous, multi-agent AI system designed to revolutionize post-operative patient care. Built with Google's Agent Development Kit (ADK), it provides proactive, empathetic, and continuous support to bridge the critical gap between hospital discharge and full recovery.

## 🏗️ Architecture

CareConnect employs a **Hierarchical Multi-Agent System** where a central Patient-Advocate-Agent acts as a supervisor, communicating with specialized backend agents via the **Agent2Agent (A2A) protocol**.

### Agent Ensemble

| Agent | Type | Role |
|-------|------|------|
| **Patient-Advocate-Agent** | LlmAgent | Primary conversational interface and supervisor |
| **Triage-Agent** | LlmAgent | Medical risk assessment and escalation |
| **Scheduler-Agent** | CustomAgent | Appointment scheduling and calendar management |
| **Pharmacy-Agent** | CustomAgent | Medication management and reminders |
| **Nurse-Notifier-Agent** | CustomAgent | Healthcare provider alerts and notifications |

## 🚀 Features

### Core Capabilities
- **Proactive Patient Engagement**: Daily check-ins with empathetic AI conversation
- **Automated Care Coordination**: Medication reminders and appointment scheduling
- **Critical Symptom Triage**: Intelligent escalation of concerning symptoms
- **Multi-Channel Notifications**: SMS, email, dashboard, and pager alerts
- **A2A Protocol Communication**: Seamless inter-agent coordination

### Key Scenarios
1. **Daily Check-in**: Routine wellness monitoring and medication reminders
2. **Symptom Triage**: Automatic escalation of concerning symptoms to healthcare providers
3. **Appointment Management**: Automated scheduling and calendar integration
4. **Medication Adherence**: Smart reminders and interaction checking

## 🛠️ Technology Stack

- **Framework**: Google Agent Development Kit (ADK) v1.0.0+
- **AI Models**: Google Gemini 2.5 Flash
- **Communication**: Agent2Agent (A2A) Protocol
- **Deployment**: Google Cloud (Vertex AI Agent Engine / Cloud Run)
- **Notifications**: Twilio SMS, SendGrid Email
- **Security**: Google Secret Manager

## 📋 Prerequisites

- Python 3.9+
- Google Cloud Project with ADK enabled
- Google ADK CLI installed
- Virtual environment (recommended)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd careconnect
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp agent/.env.example agent/.env
   # Edit agent/.env with your configuration
   ```

5. **Set up Google Cloud credentials**
   ```bash
   gcloud auth application-default login
   export GOOGLE_CLOUD_PROJECT=your-project-id
   ```

## 🚀 Quick Start

### Run with ADK Web Interface
```bash
adk web
```

### Run with ADK CLI
```bash
adk run agent
```

### Direct Python Execution
```bash
cd agent
python agent.py
```

## 🧪 Testing

### Run Demo Interactions
```bash
python -m agent.agent
# Choose option 1 for demo interaction
```

### Test Individual Agents
```bash
python -m agent.agent
# Choose option 2 for capability testing
```

### System Status Check
```bash
python -m agent.agent
# Choose option 3 for system status
```

## 📊 Agent Details

### Patient-Advocate-Agent
- **Type**: LlmAgent
- **Role**: Primary conversational interface and task coordinator
- **Key Features**:
  - Empathetic conversation management
  - Intelligent task delegation via A2A protocol
  - Patient state tracking and context management
  - Natural language understanding for healthcare scenarios

### Triage-Agent
- **Type**: LlmAgent
- **Role**: Medical risk assessment specialist
- **Key Features**:
  - Symptom analysis and risk scoring
  - Automatic escalation for critical conditions
  - Structured medical assessment output
  - Integration with Nurse-Notifier-Agent

### Scheduler-Agent
- **Type**: CustomAgent
- **Role**: Appointment and calendar management
- **Key Features**:
  - Google Calendar API integration
  - Doctor availability checking
  - Automated appointment booking
  - Reminder scheduling

### Pharmacy-Agent
- **Type**: CustomAgent
- **Role**: Medication management specialist
- **Key Features**:
  - Medication schedule tracking
  - Drug interaction checking
  - Refill management
  - Side effect monitoring

### Nurse-Notifier-Agent
- **Type**: CustomAgent
- **Role**: Healthcare provider alert system
- **Key Features**:
  - Multi-channel notifications (SMS, email, pager, dashboard)
  - Priority-based alert routing
  - Escalation management
  - Audit trail logging

## 🔄 A2A Protocol Communication

The system uses the Agent2Agent protocol for seamless communication between agents:

```python
# Example A2A call from Patient-Advocate to Triage-Agent
response = await self.a2a_client.call_agent(
    agent_name="triage_agent",
    method="assess_symptoms",
    params={
        "patient_message": message,
        "patient_context": self.patient_context
    }
)
```

## 📝 Configuration

### Environment Variables
Key configuration options in `agent/.env`:

```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-gemini-api-key

# A2A Protocol
A2A_SERVER_PORT=8080
A2A_SERVER_HOST=localhost

# Notifications
TWILIO_ACCOUNT_SID=your-twilio-sid
SENDGRID_API_KEY=your-sendgrid-key

# Features
ENABLE_A2A_PROTOCOL=true
ENABLE_REAL_NOTIFICATIONS=false
```

## 🏥 Healthcare Scenarios

### Scenario 1: Daily Check-in (Happy Path)
```
Patient: "Hi, I'm feeling pretty good today. A little sore, but better than yesterday."
System: Coordinates with Pharmacy-Agent for medication reminders and Scheduler-Agent for appointment confirmations.
```

### Scenario 2: Critical Symptom Escalation
```
Patient: "I feel terrible. I have a high fever, and the incision site is red and hot."
System: 
1. Triage-Agent assesses symptoms as CRITICAL
2. Nurse-Notifier-Agent sends urgent alerts to healthcare providers
3. Patient receives reassuring response while alerts are dispatched
```

## 🔒 Security & Privacy

- All API keys stored in Google Secret Manager
- Mock patient data only (no real PHI)
- Audit logging for all agent interactions
- Secure A2A protocol communication

## 🚀 Deployment

### Google Cloud Run
```bash
# Build and deploy
gcloud run deploy careconnect-agent \
  --source . \
  --platform managed \
  --region us-central1
```

### Vertex AI Agent Engine
```bash
# Deploy to Agent Engine
adk deploy --platform vertex-ai
```

## 📈 Monitoring & Logging

- Structured logging with correlation IDs
- Google Cloud Pub/Sub for event streaming
- BigQuery for analytics and auditing
- Real-time dashboard for system health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the ADK documentation: https://google.github.io/adk-docs/

---

**Built with ❤️ using Google's Agent Development Kit**
