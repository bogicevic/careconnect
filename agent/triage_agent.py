"""Triage Agent - Medical risk assessment specialist for CareConnect system."""

from adk.agents import LlmAgent
from adk.models import ModelConfig
from adk.a2a import A2AClient
import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)


class TriageAgent(LlmAgent):
    """
    The Triage-Agent specializes in analyzing patient messages for medical concerns
    and determining if escalation to healthcare providers is needed.
    """
    
    def __init__(self, name: str = "triage_agent"):
        # Configure the LLM for medical risk assessment
        model_config = ModelConfig(
            model_name="gemini-2.5-flash",
            temperature=0.3,  # Lower temperature for more consistent medical assessments
            max_tokens=800
        )
        
        # System instruction focused on medical triage
        system_instruction = """
        You are a Medical Triage Specialist AI for post-operative patients. Your role is to:
        
        1. ANALYZE patient messages for signs of medical complications or urgent concerns
        2. ASSESS risk levels based on reported symptoms
        3. DETERMINE if immediate healthcare provider notification is needed
        4. PROVIDE structured assessment data for other agents
        
        CRITICAL SYMPTOMS requiring immediate escalation:
        - High fever (>101°F/38.3°C)
        - Signs of infection (redness, heat, swelling, pus at incision site)
        - Severe or worsening pain
        - Shortness of breath or chest pain
        - Heavy bleeding
        - Signs of blood clots (leg swelling, pain, warmth)
        - Severe nausea/vomiting preventing medication intake
        - Confusion or altered mental state
        
        MODERATE CONCERNS requiring monitoring:
        - Mild fever
        - Moderate pain increase
        - Minor swelling
        - Medication side effects
        - Mobility concerns
        
        LOW PRIORITY:
        - General recovery questions
        - Mild discomfort within expected range
        - Medication timing questions
        - Appointment scheduling
        
        Always respond with structured JSON containing:
        - risk_level: "CRITICAL", "MODERATE", or "LOW"
        - escalate: boolean
        - symptoms_identified: list of symptoms
        - reasoning: explanation of assessment
        - recommendations: immediate actions needed
        """
        
        super().__init__(
            name=name,
            model_config=model_config,
            system_instruction=system_instruction
        )
        
        # Initialize A2A client for communicating with Nurse-Notifier-Agent
        self.a2a_client = A2AClient()
    
    async def assess_symptoms(self, patient_message: str, patient_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess patient symptoms and determine if escalation is needed.
        
        Args:
            patient_message: The patient's message describing their condition
            patient_context: Additional context about the patient
            
        Returns:
            Dict containing triage assessment results
        """
        try:
            logger.info(f"Assessing symptoms from message: {patient_message[:100]}...")
            
            # Build assessment prompt
            assessment_prompt = f"""
            PATIENT MESSAGE: "{patient_message}"
            
            PATIENT CONTEXT:
            {json.dumps(patient_context, indent=2) if patient_context else "No additional context"}
            
            Analyze this message for medical concerns and provide a structured assessment.
            Focus on post-operative complications for knee replacement surgery.
            
            Respond with valid JSON only:
            {{
                "risk_level": "CRITICAL|MODERATE|LOW",
                "escalate": true/false,
                "symptoms_identified": ["symptom1", "symptom2"],
                "reasoning": "explanation of your assessment",
                "recommendations": ["action1", "action2"],
                "urgency_score": 1-10,
                "keywords_detected": ["keyword1", "keyword2"]
            }}
            """
            
            # Get LLM assessment
            response = await self.generate_response(assessment_prompt)
            
            # Parse JSON response
            try:
                assessment = json.loads(response)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response}")
                # Fallback assessment
                assessment = {
                    "risk_level": "MODERATE",
                    "escalate": True,
                    "symptoms_identified": ["parsing_error"],
                    "reasoning": "Unable to parse assessment, escalating for safety",
                    "recommendations": ["Manual review needed"],
                    "urgency_score": 5,
                    "keywords_detected": []
                }
            
            # If escalation is needed, notify the Nurse-Notifier-Agent
            if assessment.get("escalate", False):
                logger.info("Escalation needed - calling Nurse-Notifier-Agent")
                await self._trigger_nurse_notification(patient_message, assessment, patient_context)
            
            logger.info(f"Triage assessment completed: {assessment['risk_level']} risk")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in symptom assessment: {e}")
            # Safe fallback - escalate on error
            return {
                "risk_level": "CRITICAL",
                "escalate": True,
                "symptoms_identified": ["system_error"],
                "reasoning": f"System error during assessment: {str(e)}",
                "recommendations": ["Immediate manual review required"],
                "urgency_score": 10,
                "keywords_detected": []
            }
    
    async def _trigger_nurse_notification(self, patient_message: str, assessment: Dict[str, Any], patient_context: Dict[str, Any]):
        """Trigger nurse notification via Nurse-Notifier-Agent."""
        try:
            notification_data = {
                "patient_message": patient_message,
                "triage_assessment": assessment,
                "patient_context": patient_context,
                "timestamp": self._get_current_timestamp(),
                "priority": self._map_risk_to_priority(assessment["risk_level"])
            }
            
            response = await self.a2a_client.call_agent(
                agent_name="nurse_notifier_agent",
                method="send_alert",
                params=notification_data
            )
            
            logger.info(f"Nurse notification triggered: {response}")
            
        except Exception as e:
            logger.error(f"Failed to trigger nurse notification: {e}")
    
    def _map_risk_to_priority(self, risk_level: str) -> str:
        """Map risk level to notification priority."""
        mapping = {
            "CRITICAL": "URGENT",
            "MODERATE": "HIGH",
            "LOW": "NORMAL"
        }
        return mapping.get(risk_level, "HIGH")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for notifications."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def get_triage_history(self, patient_id: str = None) -> List[Dict[str, Any]]:
        """Get triage history for a patient (placeholder for future implementation)."""
        # This would typically query a database
        return []
    
    async def update_triage_protocols(self, protocols: Dict[str, Any]) -> bool:
        """Update triage protocols (placeholder for future implementation)."""
        # This would typically update configuration
        logger.info("Triage protocols update requested")
        return True


# A2A Protocol handler for external calls
class TriageAgentA2AHandler:
    """Handler for A2A protocol calls to the Triage Agent."""
    
    def __init__(self):
        self.agent = TriageAgent()
    
    async def assess_symptoms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A call for symptom assessment."""
        patient_message = params.get("patient_message", "")
        patient_context = params.get("patient_context", {})
        
        return await self.agent.assess_symptoms(patient_message, patient_context)
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for A2A discovery."""
        return {
            "agent_name": "triage_agent",
            "agent_type": "LlmAgent",
            "capabilities": [
                {
                    "method": "assess_symptoms",
                    "description": "Assess patient symptoms for medical risk",
                    "parameters": {
                        "patient_message": "string",
                        "patient_context": "object"
                    },
                    "returns": "triage_assessment_object"
                }
            ],
            "specialization": "Medical risk assessment and triage",
            "version": "1.0.0"
        }