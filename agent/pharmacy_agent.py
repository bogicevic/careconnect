"""Pharmacy Agent - Medication management specialist for CareConnect system."""

from adk.agents import CustomAgent
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PharmacyAgent(CustomAgent):
    """
    The Pharmacy-Agent specializes in managing patient medications,
    tracking schedules, and providing medication reminders.
    """
    
    def __init__(self, name: str = "pharmacy_agent"):
        super().__init__(name=name)
        
        # Mock medication database (in real implementation, this would be a proper database)
        self.medications_db = self._initialize_mock_medications()
        self.patient_prescriptions = self._initialize_patient_prescriptions()
        
        # Medication timing and reminder settings
        self.reminder_settings = {
            "advance_minutes": [30, 5],  # Minutes before dose to send reminders
            "max_delay_hours": 2,  # Maximum delay before escalating missed dose
            "interaction_check": True,
            "allergy_check": True
        }
    
    def _initialize_mock_medications(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mock medication database."""
        return {
            "ibuprofen_600mg": {
                "name": "Ibuprofen",
                "strength": "600mg",
                "type": "NSAID",
                "common_uses": ["pain relief", "inflammation"],
                "side_effects": ["stomach upset", "dizziness"],
                "contraindications": ["kidney disease", "heart conditions"],
                "max_daily_dose": "2400mg",
                "food_requirements": "take with food"
            },
            "acetaminophen_500mg": {
                "name": "Acetaminophen",
                "strength": "500mg",
                "type": "Analgesic",
                "common_uses": ["pain relief", "fever reduction"],
                "side_effects": ["rare at normal doses"],
                "contraindications": ["liver disease"],
                "max_daily_dose": "3000mg",
                "food_requirements": "can take with or without food"
            },
            "oxycodone_5mg": {
                "name": "Oxycodone",
                "strength": "5mg",
                "type": "Opioid",
                "common_uses": ["severe pain"],
                "side_effects": ["drowsiness", "constipation", "nausea"],
                "contraindications": ["respiratory depression", "addiction history"],
                "max_daily_dose": "varies by prescription",
                "food_requirements": "can take with or without food",
                "controlled_substance": True
            },
            "cephalexin_500mg": {
                "name": "Cephalexin",
                "strength": "500mg",
                "type": "Antibiotic",
                "common_uses": ["bacterial infections"],
                "side_effects": ["diarrhea", "nausea"],
                "contraindications": ["penicillin allergy"],
                "max_daily_dose": "4000mg",
                "food_requirements": "can take with or without food",
                "course_completion": "must complete full course"
            }
        }
    
    def _initialize_patient_prescriptions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mock patient prescriptions."""
        return {
            "Elena": [
                {
                    "medication_id": "ibuprofen_600mg",
                    "prescribed_date": "2025-06-20",
                    "dosage": "600mg",
                    "frequency": "every 8 hours",
                    "duration_days": 14,
                    "instructions": "Take with food for pain and inflammation",
                    "prescriber": "Dr. Smith",
                    "refills_remaining": 2,
                    "next_dose_time": "13:00",
                    "status": "active"
                },
                {
                    "medication_id": "oxycodone_5mg",
                    "prescribed_date": "2025-06-20",
                    "dosage": "5mg",
                    "frequency": "every 6 hours as needed",
                    "duration_days": 7,
                    "instructions": "For severe pain only. Do not drive.",
                    "prescriber": "Dr. Smith",
                    "refills_remaining": 0,
                    "next_dose_time": "as needed",
                    "status": "active"
                },
                {
                    "medication_id": "cephalexin_500mg",
                    "prescribed_date": "2025-06-20",
                    "dosage": "500mg",
                    "frequency": "every 6 hours",
                    "duration_days": 10,
                    "instructions": "Complete full course to prevent infection",
                    "prescriber": "Dr. Smith",
                    "refills_remaining": 0,
                    "next_dose_time": "14:00",
                    "status": "active"
                }
            ]
        }
    
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the Pharmacy Agent.
        Handles various medication-related requests.
        """
        try:
            action = request.get("action", "manage_medications")
            
            if action == "manage_medications":
                return await self.manage_medications(request)
            elif action == "check_medication_schedule":
                return await self.check_medication_schedule(request)
            elif action == "get_medication_info":
                return await self.get_medication_info(request)
            elif action == "check_interactions":
                return await self.check_drug_interactions(request)
            elif action == "refill_request":
                return await self.process_refill_request(request)
            elif action == "medication_adherence":
                return await self.track_medication_adherence(request)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "available_actions": [
                        "manage_medications", "check_medication_schedule", "get_medication_info",
                        "check_interactions", "refill_request", "medication_adherence"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error in PharmacyAgent.invoke: {e}")
            return {
                "status": "error",
                "message": f"Pharmacy agent error: {str(e)}"
            }
    
    async def manage_medications(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main medication management method called by Patient-Advocate-Agent.
        """
        try:
            patient_message = request.get("patient_message", "")
            patient_context = request.get("patient_context", {})
            
            logger.info(f"Managing medications for message: {patient_message[:100]}...")
            
            # Analyze the message to determine what medication action is needed
            intent = await self._analyze_medication_intent(patient_message)
            
            if intent == "schedule_reminder":
                return await self._handle_medication_reminder(patient_message, patient_context)
            elif intent == "check_schedule":
                return await self._handle_schedule_check(patient_context)
            elif intent == "medication_info":
                return await self._handle_medication_info_request(patient_message, patient_context)
            elif intent == "side_effects":
                return await self._handle_side_effects_query(patient_message, patient_context)
            elif intent == "refill":
                return await self._handle_refill_request(patient_message, patient_context)
            elif intent == "missed_dose":
                return await self._handle_missed_dose(patient_message, patient_context)
            else:
                return await self._handle_general_medication_query(patient_message, patient_context)
                
        except Exception as e:
            logger.error(f"Error managing medications: {e}")
            return {
                "status": "error",
                "message": "Unable to manage medications at this time",
                "error_details": str(e)
            }
    
    async def _analyze_medication_intent(self, message: str) -> str:
        """Analyze patient message to determine medication intent."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["remind", "when", "time to take", "schedule"]):
            return "schedule_reminder"
        elif any(word in message_lower for word in ["what medications", "my pills", "prescription"]):
            return "check_schedule"
        elif any(word in message_lower for word in ["what is", "about", "information", "tell me"]):
            return "medication_info"
        elif any(word in message_lower for word in ["side effect", "reaction", "feeling", "nausea", "dizzy"]):
            return "side_effects"
        elif any(word in message_lower for word in ["refill", "running out", "need more", "pharmacy"]):
            return "refill"
        elif any(word in message_lower for word in ["missed", "forgot", "skipped", "late"]):
            return "missed_dose"
        else:
            return "general_query"
    
    async def _handle_medication_reminder(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle medication reminder requests."""
        try:
            patient_name = patient_context.get("name", "Patient")
            current_time = datetime.now()
            
            # Get patient's current medications
            prescriptions = self.patient_prescriptions.get(patient_name, [])
            active_prescriptions = [p for p in prescriptions if p["status"] == "active"]
            
            if not active_prescriptions:
                return {
                    "status": "no_medications",
                    "message": "No active medications found",
                    "medications": []
                }
            
            # Check which medications are due soon
            upcoming_doses = []
            for prescription in active_prescriptions:
                next_dose_info = await self._calculate_next_dose(prescription, current_time)
                if next_dose_info:
                    upcoming_doses.append(next_dose_info)
            
            # Sort by time
            upcoming_doses.sort(key=lambda x: x.get("time_until_minutes", float('inf')))
            
            return {
                "status": "reminder_set",
                "message": f"Medication reminders for {len(upcoming_doses)} medications",
                "upcoming_doses": upcoming_doses,
                "next_medication": upcoming_doses[0] if upcoming_doses else None,
                "total_active_medications": len(active_prescriptions)
            }
            
        except Exception as e:
            logger.error(f"Error handling medication reminder: {e}")
            return {
                "status": "error",
                "message": "Unable to set medication reminders",
                "error_details": str(e)
            }
    
    async def _handle_schedule_check(self, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle medication schedule check requests."""
        try:
            patient_name = patient_context.get("name", "Patient")
            prescriptions = self.patient_prescriptions.get(patient_name, [])
            active_prescriptions = [p for p in prescriptions if p["status"] == "active"]
            
            if not active_prescriptions:
                return {
                    "status": "no_medications",
                    "message": "No active medications found",
                    "medications": []
                }
            
            # Build detailed medication schedule
            medication_schedule = []
            for prescription in active_prescriptions:
                med_info = self.medications_db.get(prescription["medication_id"], {})
                
                schedule_item = {
                    "medication_name": med_info.get("name", "Unknown"),
                    "strength": med_info.get("strength", ""),
                    "dosage": prescription["dosage"],
                    "frequency": prescription["frequency"],
                    "instructions": prescription["instructions"],
                    "next_dose_time": prescription["next_dose_time"],
                    "refills_remaining": prescription["refills_remaining"],
                    "prescriber": prescription["prescriber"],
                    "food_requirements": med_info.get("food_requirements", "")
                }
                medication_schedule.append(schedule_item)
            
            return {
                "status": "schedule_found",
                "message": f"Current medication schedule for {patient_name}",
                "medications": medication_schedule,
                "total_medications": len(medication_schedule)
            }
            
        except Exception as e:
            logger.error(f"Error checking medication schedule: {e}")
            return {
                "status": "error",
                "message": "Unable to check medication schedule",
                "error_details": str(e)
            }
    
    async def _handle_medication_info_request(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for medication information."""
        try:
            # Extract medication name from message (simplified)
            medication_mentioned = None
            for med_id, med_info in self.medications_db.items():
                if med_info["name"].lower() in message.lower():
                    medication_mentioned = med_info
                    break
            
            if not medication_mentioned:
                return {
                    "status": "medication_not_found",
                    "message": "Could not identify specific medication in your question",
                    "suggestion": "Please specify which medication you're asking about"
                }
            
            return {
                "status": "info_provided",
                "message": f"Information about {medication_mentioned['name']}",
                "medication_info": {
                    "name": medication_mentioned["name"],
                    "type": medication_mentioned["type"],
                    "common_uses": medication_mentioned["common_uses"],
                    "food_requirements": medication_mentioned["food_requirements"],
                    "max_daily_dose": medication_mentioned["max_daily_dose"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error providing medication info: {e}")
            return {
                "status": "error",
                "message": "Unable to provide medication information",
                "error_details": str(e)
            }
    
    async def _handle_side_effects_query(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle side effects and adverse reaction queries."""
        try:
            patient_name = patient_context.get("name", "Patient")
            prescriptions = self.patient_prescriptions.get(patient_name, [])
            
            # Check for concerning side effects that might need escalation
            concerning_symptoms = ["severe", "chest pain", "difficulty breathing", "swelling", "rash", "allergic"]
            is_concerning = any(symptom in message.lower() for symptom in concerning_symptoms)
            
            if is_concerning:
                return {
                    "status": "concerning_side_effects",
                    "message": "Concerning symptoms reported - medical evaluation recommended",
                    "escalate": True,
                    "immediate_actions": [
                        "Stop medication if severe reaction",
                        "Contact healthcare provider immediately",
                        "Seek emergency care if breathing difficulties"
                    ]
                }
            
            # Provide general side effect information
            side_effects_info = []
            for prescription in prescriptions:
                if prescription["status"] == "active":
                    med_info = self.medications_db.get(prescription["medication_id"], {})
                    if med_info:
                        side_effects_info.append({
                            "medication": med_info["name"],
                            "common_side_effects": med_info.get("side_effects", []),
                            "instructions": prescription["instructions"]
                        })
            
            return {
                "status": "side_effects_info",
                "message": "Side effect information for your medications",
                "medications": side_effects_info,
                "general_advice": "Contact your doctor if side effects persist or worsen"
            }
            
        except Exception as e:
            logger.error(f"Error handling side effects query: {e}")
            return {
                "status": "error",
                "message": "Unable to provide side effects information",
                "error_details": str(e)
            }
    
    async def _handle_refill_request(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle medication refill requests."""
        try:
            patient_name = patient_context.get("name", "Patient")
            prescriptions = self.patient_prescriptions.get(patient_name, [])
            
            refill_needed = []
            for prescription in prescriptions:
                if prescription["status"] == "active" and prescription["refills_remaining"] > 0:
                    med_info = self.medications_db.get(prescription["medication_id"], {})
                    refill_needed.append({
                        "medication": med_info.get("name", "Unknown"),
                        "refills_remaining": prescription["refills_remaining"],
                        "prescriber": prescription["prescriber"]
                    })
            
            if not refill_needed:
                return {
                    "status": "no_refills_available",
                    "message": "No refills available for current medications",
                    "action_needed": "Contact prescriber for new prescription"
                }
            
            return {
                "status": "refill_available",
                "message": f"Refills available for {len(refill_needed)} medications",
                "refillable_medications": refill_needed,
                "next_steps": ["Contact pharmacy to process refill", "Ensure pickup within 30 days"]
            }
            
        except Exception as e:
            logger.error(f"Error handling refill request: {e}")
            return {
                "status": "error",
                "message": "Unable to process refill request",
                "error_details": str(e)
            }
    
    async def _handle_missed_dose(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missed dose situations."""
        try:
            return {
                "status": "missed_dose_guidance",
                "message": "Guidance for missed medication dose",
                "general_advice": [
                    "Take the missed dose as soon as you remember",
                    "If it's almost time for the next dose, skip the missed dose",
                    "Never double up on doses",
                    "Contact your healthcare provider if you frequently miss doses"
                ],
                "specific_instructions": "Follow the specific instructions provided with each medication"
            }
            
        except Exception as e:
            logger.error(f"Error handling missed dose: {e}")
            return {
                "status": "error",
                "message": "Unable to provide missed dose guidance",
                "error_details": str(e)
            }
    
    async def _handle_general_medication_query(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general medication queries."""
        return {
            "status": "general_info",
            "message": "General medication management information",
            "available_services": [
                "Medication schedule and reminders",
                "Drug information and side effects",
                "Refill management",
                "Missed dose guidance",
                "Drug interaction checking"
            ],
            "contact_info": "For specific medical questions, contact your healthcare provider"
        }
    
    async def _calculate_next_dose(self, prescription: Dict[str, Any], current_time: datetime) -> Optional[Dict[str, Any]]:
        """Calculate when the next dose is due."""
        try:
            next_dose_time = prescription.get("next_dose_time", "")
            
            if next_dose_time == "as needed":
                return {
                    "medication": prescription["medication_id"],
                    "next_dose": "as needed",
                    "time_until_minutes": None,
                    "instructions": prescription["instructions"]
                }
            
            # Parse time (simplified - assumes HH:MM format)
            if ":" in next_dose_time:
                hour, minute = map(int, next_dose_time.split(":"))
                next_dose_datetime = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, schedule for tomorrow
                if next_dose_datetime <= current_time:
                    next_dose_datetime += timedelta(days=1)
                
                time_until = next_dose_datetime - current_time
                time_until_minutes = int(time_until.total_seconds() / 60)
                
                return {
                    "medication": prescription["medication_id"],
                    "next_dose": next_dose_time,
                    "time_until_minutes": time_until_minutes,
                    "instructions": prescription["instructions"],
                    "dosage": prescription["dosage"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating next dose: {e}")
            return None
    
    async def check_medication_schedule(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check medication schedule for a patient."""
        patient_context = request.get("patient_context", {})
        return await self._handle_schedule_check(patient_context)
    
    async def get_medication_info(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific medication."""
        medication_name = request.get("medication_name", "")
        
        for med_id, med_info in self.medications_db.items():
            if med_info["name"].lower() == medication_name.lower():
                return {
                    "status": "found",
                    "medication": med_info
                }
        
        return {
            "status": "not_found",
            "message": f"Medication '{medication_name}' not found in database"
        }
    
    async def check_drug_interactions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check for drug interactions (mock implementation)."""
        medications = request.get("medications", [])
        
        # Mock interaction check
        return {
            "status": "checked",
            "interactions_found": False,
            "message": "No significant interactions found",
            "medications_checked": medications
        }
    
    async def process_refill_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a refill request."""
        patient_context = request.get("patient_context", {})
        return await self._handle_refill_request("", patient_context)
    
    async def track_medication_adherence(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Track medication adherence (mock implementation)."""
        patient_context = request.get("patient_context", {})
        patient_name = patient_context.get("name", "Patient")
        
        return {
            "status": "tracked",
            "patient": patient_name,
            "adherence_rate": "85%",
            "missed_doses_last_week": 2,
            "recommendations": [
                "Set phone reminders for medication times",
                "Use a pill organizer",
                "Take medications at the same time daily"
            ]
        }


# A2A Protocol handler for external calls
class PharmacyAgentA2AHandler:
    """Handler for A2A protocol calls to the Pharmacy Agent."""
    
    def __init__(self):
        self.agent = PharmacyAgent()
    
    async def manage_medications(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A call for medication management."""
        return await self.agent.manage_medications(params)
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for A2A discovery."""
        return {
            "agent_name": "pharmacy_agent",
            "agent_type": "CustomAgent",
            "capabilities": [
                {
                    "method": "manage_medications",
                    "description": "Manage patient medications and schedules",
                    "parameters": {
                        "patient_message": "string",
                        "patient_context": "object"
                    },
                    "returns": "medication_management_object"
                },
                {
                    "method": "check_medication_schedule",
                    "description": "Check patient medication schedule",
                    "parameters": {
                        "patient_context": "object"
                    },
                    "returns": "medication_schedule_object"
                },
                {
                    "method": "check_drug_interactions",
                    "description": "Check for drug interactions",
                    "parameters": {
                        "medications": "array"
                    },
                    "returns": "interaction_check_object"
                }
            ],
            "specialization": "Medication management and pharmacy services",
            "version": "1.0.0"
        }