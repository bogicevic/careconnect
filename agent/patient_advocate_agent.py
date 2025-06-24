"""Patient Advocate Agent - Main supervisor agent for CareConnect system."""

from adk.agents import LlmAgent
from adk.models import ModelConfig
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PatientAdvocateAgent(LlmAgent):
    """
    The Patient-Advocate-Agent acts as the primary conversational interface
    and supervisor in the CareConnect multi-agent system. It delegates tasks
    to specialist agents via the A2A protocol.
    """
    
    def __init__(self, name: str = "patient_advocate"):
        # Configure the LLM with empathetic healthcare instructions
        model_config = ModelConfig(
            model_name="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        # System instruction focused on empathy and healthcare
        system_instruction = """
        You are Elena's Patient Advocate, a compassionate AI healthcare assistant 
        specializing in post-operative care. Your role is to:
        
        1. EMPATHY FIRST: Always respond with warmth, understanding, and reassurance
        2. ACTIVE LISTENING: Carefully analyze what the patient says for both explicit and implicit concerns
        3. TASK DELEGATION: Use your specialist agent team via A2A protocol for specific tasks:
           - Scheduler-Agent: For appointment scheduling and calendar management
           - Pharmacy-Agent: For medication reminders and prescription status
           - Triage-Agent: For medical risk assessment of concerning symptoms
           - Nurse-Notifier-Agent: For urgent alerts to healthcare providers
        
        4. CONVERSATION FLOW: Keep conversations natural and patient-focused
        5. SAFETY: Always escalate concerning symptoms through the Triage-Agent
        
        Remember: You are Elena's advocate and support system during her recovery.
        Be proactive, caring, and thorough in addressing her needs.
        """
        
        super().__init__(
            name=name,
            model_config=model_config,
            system_instruction=system_instruction
        )
        
        # Initialize direct agent communication (simplified for demo)
        self.specialist_agents = {}
        
        # Track patient state and conversation context
        self.patient_context = {
            "name": "Elena",
            "condition": "post-operative knee replacement",
            "concerns": [],
            "last_checkin": None,
            "medication_schedule": [],
            "appointments": []
        }
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process patient message and coordinate with specialist agents as needed.
        """
        try:
            logger.info(f"Processing patient message: {message[:100]}...")
            
            # Analyze message for keywords that require specialist agent involvement
            needs_triage = await self._analyze_for_triage_keywords(message)
            needs_scheduling = await self._analyze_for_scheduling_keywords(message)
            needs_pharmacy = await self._analyze_for_medication_keywords(message)
            
            # Delegate to specialist agents via A2A protocol
            specialist_responses = {}
            
            if needs_triage:
                logger.info("Delegating to Triage-Agent for medical assessment")
                specialist_responses["triage"] = await self._call_triage_agent(message)
            
            if needs_scheduling:
                logger.info("Delegating to Scheduler-Agent for appointment management")
                specialist_responses["scheduler"] = await self._call_scheduler_agent(message)
            
            if needs_pharmacy:
                logger.info("Delegating to Pharmacy-Agent for medication management")
                specialist_responses["pharmacy"] = await self._call_pharmacy_agent(message)
            
            # Generate empathetic response incorporating specialist feedback
            response = await self._generate_response(message, specialist_responses)
            
            # Update patient context
            self._update_patient_context(message, specialist_responses)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm sorry, I'm having some technical difficulties. Let me try to help you in a moment."
    
    async def _analyze_for_triage_keywords(self, message: str) -> bool:
        """Analyze message for medical concern keywords."""
        triage_keywords = [
            "fever", "high fever", "pain", "severe pain", "red", "hot", "swollen",
            "infection", "bleeding", "dizzy", "nausea", "vomiting", "shortness of breath",
            "chest pain", "terrible", "awful", "emergency", "urgent", "help"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in triage_keywords)
    
    async def _analyze_for_scheduling_keywords(self, message: str) -> bool:
        """Analyze message for appointment/scheduling keywords."""
        scheduling_keywords = [
            "appointment", "schedule", "doctor", "visit", "follow-up", "check-up",
            "calendar", "when", "time", "date", "available", "book"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in scheduling_keywords)
    
    async def _analyze_for_medication_keywords(self, message: str) -> bool:
        """Analyze message for medication keywords."""
        medication_keywords = [
            "medication", "medicine", "pill", "prescription", "dose", "take",
            "pharmacy", "refill", "pain medication", "antibiotic", "remind"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in medication_keywords)
    
    async def _call_triage_agent(self, message: str) -> Dict[str, Any]:
        """Call Triage-Agent for symptom assessment."""
        try:
            # For demo purposes, provide mock triage response
            # In full implementation, this would use A2A protocol
            
            # Simple keyword-based triage assessment
            concerning_keywords = ["fever", "high fever", "red", "hot", "swollen", "terrible", "awful", "severe pain"]
            is_concerning = any(keyword in message.lower() for keyword in concerning_keywords)
            
            if is_concerning:
                return {
                    "status": "assessment_complete",
                    "risk_level": "CRITICAL",
                    "escalate": True,
                    "symptoms_identified": ["fever", "infection signs"],
                    "reasoning": "Patient reports concerning symptoms that may indicate post-operative complications",
                    "recommendations": ["Immediate healthcare provider notification", "Monitor symptoms closely"],
                    "urgency_score": 9
                }
            else:
                return {
                    "status": "assessment_complete",
                    "risk_level": "LOW",
                    "escalate": False,
                    "symptoms_identified": ["general discomfort"],
                    "reasoning": "Symptoms appear within normal recovery range",
                    "recommendations": ["Continue current care plan", "Monitor progress"],
                    "urgency_score": 3
                }
                
        except Exception as e:
            logger.error(f"Error calling Triage-Agent: {e}")
            return {"status": "error", "message": "Unable to assess symptoms at this time"}
    
    async def _call_scheduler_agent(self, message: str) -> Dict[str, Any]:
        """Call Scheduler-Agent for appointment management."""
        try:
            # Mock scheduler response for demo
            if any(word in message.lower() for word in ["appointment", "schedule", "when", "doctor"]):
                return {
                    "status": "scheduled",
                    "message": "Follow-up appointment confirmed",
                    "appointment": {
                        "doctor": "Dr. Smith",
                        "date": "2025-07-01",
                        "time": "10:00",
                        "type": "Follow-up"
                    },
                    "calendar_added": True,
                    "reminder_set": True
                }
            else:
                return {
                    "status": "no_action_needed",
                    "message": "No scheduling action required"
                }
                
        except Exception as e:
            logger.error(f"Error calling Scheduler-Agent: {e}")
            return {"status": "error", "message": "Unable to manage appointments at this time"}
    
    async def _call_pharmacy_agent(self, message: str) -> Dict[str, Any]:
        """Call Pharmacy-Agent for medication management."""
        try:
            # Mock pharmacy response for demo
            if any(word in message.lower() for word in ["medication", "medicine", "pill", "dose"]):
                return {
                    "status": "reminder_set",
                    "message": "Medication reminders updated",
                    "upcoming_doses": [
                        {
                            "medication": "Ibuprofen 600mg",
                            "next_dose": "13:00",
                            "instructions": "Take with food"
                        },
                        {
                            "medication": "Cephalexin 500mg",
                            "next_dose": "14:00",
                            "instructions": "Complete full course"
                        }
                    ],
                    "total_active_medications": 3
                }
            else:
                return {
                    "status": "no_action_needed",
                    "message": "No medication action required"
                }
                
        except Exception as e:
            logger.error(f"Error calling Pharmacy-Agent: {e}")
            return {"status": "error", "message": "Unable to manage medications at this time"}
    
    async def _generate_response(self, message: str, specialist_responses: Dict[str, Any]) -> str:
        """Generate empathetic response incorporating specialist agent feedback."""
        
        # Build context for LLM response generation
        context_prompt = f"""
        Patient Message: "{message}"
        
        Specialist Agent Responses:
        {self._format_specialist_responses(specialist_responses)}
        
        Patient Context:
        - Name: {self.patient_context['name']}
        - Condition: {self.patient_context['condition']}
        - Recent Concerns: {', '.join(self.patient_context['concerns'][-3:]) if self.patient_context['concerns'] else 'None'}
        
        Generate a warm, empathetic response that:
        1. Acknowledges the patient's message
        2. Incorporates relevant information from specialist agents
        3. Provides reassurance and next steps
        4. Maintains a caring, professional tone
        """
        
        # Use the LLM to generate the response
        response = await self.generate_response(context_prompt)
        return response
    
    def _format_specialist_responses(self, responses: Dict[str, Any]) -> str:
        """Format specialist responses for context."""
        if not responses:
            return "No specialist consultation needed."
        
        formatted = []
        for agent, response in responses.items():
            formatted.append(f"- {agent.title()}: {response}")
        
        return "\n".join(formatted)
    
    def _update_patient_context(self, message: str, specialist_responses: Dict[str, Any]):
        """Update patient context based on conversation."""
        # Add any concerns mentioned
        if specialist_responses.get("triage"):
            self.patient_context["concerns"].append(message[:100])
        
        # Update medication info if pharmacy agent responded
        if specialist_responses.get("pharmacy"):
            pharmacy_response = specialist_responses["pharmacy"]
            if "medications" in pharmacy_response:
                self.patient_context["medication_schedule"] = pharmacy_response["medications"]
        
        # Update appointment info if scheduler agent responded
        if specialist_responses.get("scheduler"):
            scheduler_response = specialist_responses["scheduler"]
            if "appointments" in scheduler_response:
                self.patient_context["appointments"] = scheduler_response["appointments"]
    
    def get_patient_context(self) -> Dict[str, Any]:
        """Get current patient context."""
        return self.patient_context.copy()
    
    def update_patient_info(self, updates: Dict[str, Any]):
        """Update patient information."""
        self.patient_context.update(updates)