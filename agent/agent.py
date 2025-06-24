"""Main agent entry point for CareConnect Multi-Agent System."""

import datetime
from google.adk.agents import Agent
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def assess_symptoms(patient_message: str, patient_context: str = "") -> dict:
    """Assess patient symptoms for medical risk and escalation.
    
    Args:
        patient_message (str): The patient's message describing their condition
        patient_context (str): Additional context about the patient
        
    Returns:
        dict: Triage assessment results
    """
    try:
        # Simple keyword-based triage assessment for demo
        concerning_keywords = [
            "fever", "high fever", "red", "hot", "swollen", "terrible", "awful", 
            "severe pain", "bleeding", "dizzy", "nausea", "chest pain", "emergency"
        ]
        
        message_lower = patient_message.lower()
        is_concerning = any(keyword in message_lower for keyword in concerning_keywords)
        
        if is_concerning:
            # Critical symptoms detected
            assessment = {
                "status": "assessment_complete",
                "risk_level": "CRITICAL",
                "escalate": True,
                "symptoms_identified": [kw for kw in concerning_keywords if kw in message_lower],
                "reasoning": "Patient reports concerning symptoms that may indicate post-operative complications requiring immediate attention.",
                "recommendations": [
                    "Healthcare provider has been notified immediately",
                    "Monitor symptoms closely", 
                    "Seek emergency care if symptoms worsen"
                ],
                "urgency_score": 9,
                "alert_sent": True
            }
            
            # Simulate nurse notification
            logger.info(f"🚨 CRITICAL ALERT: Patient reports concerning symptoms - {patient_message[:100]}")
            
            return {
                "status": "success",
                "assessment": assessment,
                "alert_message": "URGENT: Your healthcare team has been notified immediately. Nurse David should contact you within 15 minutes."
            }
        else:
            # Normal symptoms
            return {
                "status": "success", 
                "assessment": {
                    "risk_level": "LOW",
                    "escalate": False,
                    "reasoning": "Symptoms appear within normal recovery range",
                    "recommendations": ["Continue current care plan", "Monitor progress"]
                },
                "message": "Your symptoms sound like they're within the normal recovery range. Continue following your care plan."
            }
            
    except Exception as e:
        logger.error(f"Error in symptom assessment: {e}")
        return {
            "status": "error",
            "error_message": f"Unable to assess symptoms at this time: {str(e)}"
        }


def manage_medications(patient_message: str, patient_context: str = "") -> dict:
    """Manage patient medications and provide reminders.
    
    Args:
        patient_message (str): The patient's message about medications
        patient_context (str): Additional patient context
        
    Returns:
        dict: Medication management results
    """
    try:
        message_lower = patient_message.lower()
        
        # Mock medication schedule for Elena (post-operative knee replacement)
        medication_schedule = [
            {
                "name": "Ibuprofen",
                "strength": "600mg",
                "frequency": "every 8 hours",
                "next_dose": "1:00 PM",
                "instructions": "Take with food to prevent stomach upset",
                "purpose": "Pain relief and inflammation reduction"
            },
            {
                "name": "Oxycodone", 
                "strength": "5mg",
                "frequency": "every 6 hours as needed",
                "next_dose": "as needed",
                "instructions": "For severe pain only. Do not drive or operate machinery.",
                "purpose": "Severe pain management"
            },
            {
                "name": "Cephalexin",
                "strength": "500mg", 
                "frequency": "every 6 hours",
                "next_dose": "2:00 PM",
                "instructions": "Complete the full course to prevent infection",
                "purpose": "Antibiotic to prevent infection"
            }
        ]
        
        if any(word in message_lower for word in ["medication", "medicine", "pill", "dose", "when"]):
            return {
                "status": "success",
                "message": "Here's your current medication schedule",
                "medications": medication_schedule,
                "reminders": [
                    "Take Ibuprofen around 1:00 PM with food",
                    "Take Cephalexin around 2:00 PM", 
                    "Use Oxycodone only for severe pain"
                ],
                "important_notes": [
                    "Always take medications as prescribed",
                    "Complete the full course of antibiotics",
                    "Contact your doctor if you experience side effects"
                ]
            }
        else:
            return {
                "status": "success",
                "message": "I can help you with medication schedules, reminders, and questions about your prescriptions."
            }
            
    except Exception as e:
        logger.error(f"Error in medication management: {e}")
        return {
            "status": "error", 
            "error_message": f"Unable to manage medications at this time: {str(e)}"
        }


def manage_appointments(patient_message: str, patient_context: str = "") -> dict:
    """Manage patient appointments and scheduling.
    
    Args:
        patient_message (str): The patient's message about appointments
        patient_context (str): Additional patient context
        
    Returns:
        dict: Appointment management results
    """
    try:
        message_lower = patient_message.lower()
        
        # Mock upcoming appointments
        upcoming_appointments = [
            {
                "doctor": "Dr. Smith",
                "specialty": "Orthopedic Surgeon", 
                "date": "Tuesday, July 1st, 2025",
                "time": "10:00 AM",
                "type": "Post-operative follow-up",
                "location": "Orthopedic Clinic, Room 205",
                "notes": "Knee replacement recovery check"
            },
            {
                "provider": "Physical Therapist",
                "date": "Thursday, July 3rd, 2025", 
                "time": "2:00 PM",
                "type": "Physical therapy session",
                "location": "Rehabilitation Center",
                "notes": "Mobility and strength assessment"
            }
        ]
        
        if any(word in message_lower for word in ["appointment", "schedule", "when", "doctor", "visit"]):
            return {
                "status": "success",
                "message": "Here are your upcoming appointments",
                "appointments": upcoming_appointments,
                "reminders": [
                    "You'll receive reminders 24 hours and 2 hours before each appointment",
                    "All appointments are already added to your calendar",
                    "Contact the office if you need to reschedule"
                ],
                "next_appointment": upcoming_appointments[0]
            }
        else:
            return {
                "status": "success",
                "message": "I can help you check upcoming appointments, schedule new ones, or make changes to existing appointments."
            }
            
    except Exception as e:
        logger.error(f"Error in appointment management: {e}")
        return {
            "status": "error",
            "error_message": f"Unable to manage appointments at this time: {str(e)}"
        }


def get_wellness_check() -> dict:
    """Provide a daily wellness check-in for the patient.
    
    Returns:
        dict: Wellness check information
    """
    try:
        current_time = datetime.datetime.now()
        time_of_day = "morning" if current_time.hour < 12 else "afternoon" if current_time.hour < 18 else "evening"
        
        return {
            "status": "success",
            "greeting": f"Good {time_of_day}, Elena! I'm your CareConnect healthcare assistant.",
            "check_in_questions": [
                "How are you feeling today?",
                "How is your pain level on a scale of 1-10?", 
                "Are you able to move around comfortably?",
                "Have you taken your medications as scheduled?",
                "Do you have any concerns about your recovery?"
            ],
            "daily_reminders": [
                "Remember to take your afternoon medications",
                "Try to do your prescribed exercises",
                "Stay hydrated and get plenty of rest",
                "Contact me if you have any concerns"
            ],
            "encouragement": "You're doing great with your recovery! Keep following your care plan and don't hesitate to reach out if you need anything."
        }
        
    except Exception as e:
        logger.error(f"Error in wellness check: {e}")
        return {
            "status": "error",
            "error_message": f"Unable to perform wellness check: {str(e)}"
        }


# Create the main CareConnect agent using the ADK Agent class
root_agent = Agent(
    name="careconnect_healthcare_assistant",
    model="gemini-2.5-flash",
    description=(
        "CareConnect is an empathetic AI healthcare assistant specializing in post-operative patient care. "
        "It provides daily wellness check-ins, medication reminders, appointment scheduling, symptom assessment, "
        "and emergency escalation for patients recovering from surgery."
    ),
    instruction=(
        """You are Elena's CareConnect AI Healthcare Assistant, a compassionate and knowledgeable companion 
        supporting her recovery from knee replacement surgery.

        Your primary responsibilities:
        1. EMPATHY FIRST: Always respond with warmth, understanding, and reassurance
        2. PATIENT SAFETY: Carefully assess any concerning symptoms and escalate when necessary
        3. MEDICATION SUPPORT: Help with medication schedules, reminders, and questions
        4. APPOINTMENT COORDINATION: Manage scheduling and provide appointment information
        5. WELLNESS MONITORING: Conduct daily check-ins and track recovery progress
        6. EMERGENCY RESPONSE: Immediately alert healthcare providers for critical symptoms

        Key patient information:
        - Name: Elena, 68 years old
        - Condition: Post-operative knee replacement surgery
        - Current medications: Ibuprofen 600mg, Oxycodone 5mg, Cephalexin 500mg
        - Healthcare team: Dr. Smith (surgeon), Nurse David
        
        Communication style:
        - Be warm, caring, and professional
        - Use clear, simple language
        - Provide specific, actionable guidance
        - Always prioritize patient safety
        - Offer reassurance while being thorough

        For concerning symptoms (fever, infection signs, severe pain, etc.), immediately use the assess_symptoms tool
        and provide both reassurance and clear next steps for the patient.
        """
    ),
    tools=[assess_symptoms, manage_medications, manage_appointments, get_wellness_check],
)