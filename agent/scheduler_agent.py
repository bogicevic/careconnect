"""Scheduler Agent - Appointment management specialist for CareConnect system."""

from adk.agents import CustomAgent
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class SchedulerAgent(CustomAgent):
    """
    The Scheduler-Agent specializes in managing patient appointments,
    integrating with Google Calendar API for scheduling and reminders.
    """
    
    def __init__(self, name: str = "scheduler_agent"):
        super().__init__(name=name)
        
        # Mock appointment database (in real implementation, this would be a proper database)
        self.appointments_db = []
        self.doctors_schedule = self._initialize_mock_doctors_schedule()
        
        # Patient-specific scheduling preferences
        self.scheduling_preferences = {
            "preferred_times": ["10:00", "14:00", "16:00"],
            "preferred_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "advance_notice_days": 7,
            "reminder_hours": [24, 2]  # Hours before appointment to send reminders
        }
    
    def _initialize_mock_doctors_schedule(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize mock doctor availability schedule."""
        return {
            "Dr. Smith": [
                {"date": "2025-07-01", "time": "10:00", "available": True},
                {"date": "2025-07-01", "time": "14:00", "available": True},
                {"date": "2025-07-02", "time": "10:00", "available": False},
                {"date": "2025-07-02", "time": "14:00", "available": True},
                {"date": "2025-07-03", "time": "10:00", "available": True},
                {"date": "2025-07-03", "time": "16:00", "available": True},
            ],
            "Dr. Johnson": [
                {"date": "2025-07-01", "time": "09:00", "available": True},
                {"date": "2025-07-01", "time": "15:00", "available": True},
                {"date": "2025-07-02", "time": "09:00", "available": True},
                {"date": "2025-07-02", "time": "15:00", "available": False},
            ]
        }
    
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the Scheduler Agent.
        Handles various scheduling-related requests.
        """
        try:
            action = request.get("action", "manage_appointments")
            
            if action == "manage_appointments":
                return await self.manage_appointments(request)
            elif action == "check_availability":
                return await self.check_doctor_availability(request)
            elif action == "schedule_appointment":
                return await self.schedule_appointment(request)
            elif action == "get_upcoming_appointments":
                return await self.get_upcoming_appointments(request)
            elif action == "cancel_appointment":
                return await self.cancel_appointment(request)
            elif action == "reschedule_appointment":
                return await self.reschedule_appointment(request)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "available_actions": [
                        "manage_appointments", "check_availability", "schedule_appointment",
                        "get_upcoming_appointments", "cancel_appointment", "reschedule_appointment"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error in SchedulerAgent.invoke: {e}")
            return {
                "status": "error",
                "message": f"Scheduler agent error: {str(e)}"
            }
    
    async def manage_appointments(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main appointment management method called by Patient-Advocate-Agent.
        """
        try:
            patient_message = request.get("patient_message", "")
            patient_context = request.get("patient_context", {})
            
            logger.info(f"Managing appointments for message: {patient_message[:100]}...")
            
            # Analyze the message to determine what scheduling action is needed
            intent = await self._analyze_scheduling_intent(patient_message)
            
            if intent == "schedule_new":
                return await self._handle_schedule_new_appointment(patient_message, patient_context)
            elif intent == "check_existing":
                return await self._handle_check_existing_appointments(patient_context)
            elif intent == "reschedule":
                return await self._handle_reschedule_request(patient_message, patient_context)
            elif intent == "cancel":
                return await self._handle_cancel_request(patient_message, patient_context)
            else:
                return await self._handle_general_scheduling_query(patient_message, patient_context)
                
        except Exception as e:
            logger.error(f"Error managing appointments: {e}")
            return {
                "status": "error",
                "message": "Unable to manage appointments at this time",
                "error_details": str(e)
            }
    
    async def _analyze_scheduling_intent(self, message: str) -> str:
        """Analyze patient message to determine scheduling intent."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["schedule", "book", "make appointment", "need to see"]):
            return "schedule_new"
        elif any(word in message_lower for word in ["when is", "what time", "upcoming", "next appointment"]):
            return "check_existing"
        elif any(word in message_lower for word in ["reschedule", "change", "move", "different time"]):
            return "reschedule"
        elif any(word in message_lower for word in ["cancel", "can't make it", "unable to attend"]):
            return "cancel"
        else:
            return "general_query"
    
    async def _handle_schedule_new_appointment(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to schedule a new appointment."""
        try:
            # For post-operative care, typically schedule follow-up with surgeon
            doctor = "Dr. Smith"  # Default surgeon for knee replacement follow-up
            
            # Find next available slot
            available_slots = await self._find_available_slots(doctor, days_ahead=7)
            
            if not available_slots:
                return {
                    "status": "no_availability",
                    "message": "No available slots found in the next week",
                    "doctor": doctor,
                    "suggested_action": "Check availability for following week"
                }
            
            # Book the first available preferred slot
            best_slot = available_slots[0]
            appointment = await self._book_appointment(doctor, best_slot, patient_context)
            
            return {
                "status": "scheduled",
                "message": f"Follow-up appointment scheduled with {doctor}",
                "appointment": appointment,
                "calendar_added": True,
                "reminder_set": True
            }
            
        except Exception as e:
            logger.error(f"Error scheduling new appointment: {e}")
            return {
                "status": "error",
                "message": "Unable to schedule appointment",
                "error_details": str(e)
            }
    
    async def _handle_check_existing_appointments(self, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to check existing appointments."""
        try:
            patient_name = patient_context.get("name", "Patient")
            upcoming_appointments = await self._get_patient_appointments(patient_name)
            
            if not upcoming_appointments:
                return {
                    "status": "no_appointments",
                    "message": "No upcoming appointments found",
                    "appointments": []
                }
            
            return {
                "status": "found",
                "message": f"Found {len(upcoming_appointments)} upcoming appointment(s)",
                "appointments": upcoming_appointments,
                "next_appointment": upcoming_appointments[0] if upcoming_appointments else None
            }
            
        except Exception as e:
            logger.error(f"Error checking appointments: {e}")
            return {
                "status": "error",
                "message": "Unable to check appointments",
                "error_details": str(e)
            }
    
    async def _find_available_slots(self, doctor: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Find available appointment slots for a doctor."""
        available_slots = []
        doctor_schedule = self.doctors_schedule.get(doctor, [])
        
        for slot in doctor_schedule:
            if slot["available"]:
                # Check if slot is within the requested timeframe
                slot_date = datetime.strptime(slot["date"], "%Y-%m-%d")
                if slot_date <= datetime.now() + timedelta(days=days_ahead):
                    available_slots.append({
                        "doctor": doctor,
                        "date": slot["date"],
                        "time": slot["time"],
                        "datetime": f"{slot['date']} {slot['time']}"
                    })
        
        # Sort by date and time
        available_slots.sort(key=lambda x: x["datetime"])
        return available_slots
    
    async def _book_appointment(self, doctor: str, slot: Dict[str, Any], patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Book an appointment slot."""
        appointment = {
            "id": f"apt_{len(self.appointments_db) + 1}",
            "patient_name": patient_context.get("name", "Patient"),
            "doctor": doctor,
            "date": slot["date"],
            "time": slot["time"],
            "type": "Follow-up",
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "notes": "Post-operative knee replacement follow-up"
        }
        
        # Add to appointments database
        self.appointments_db.append(appointment)
        
        # Mark slot as unavailable
        doctor_schedule = self.doctors_schedule.get(doctor, [])
        for schedule_slot in doctor_schedule:
            if schedule_slot["date"] == slot["date"] and schedule_slot["time"] == slot["time"]:
                schedule_slot["available"] = False
                break
        
        # In real implementation, this would call Google Calendar API
        await self._add_to_google_calendar(appointment)
        
        logger.info(f"Appointment booked: {appointment['id']}")
        return appointment
    
    async def _add_to_google_calendar(self, appointment: Dict[str, Any]) -> bool:
        """Add appointment to Google Calendar (mock implementation)."""
        try:
            # Mock Google Calendar API call
            logger.info(f"Adding appointment to Google Calendar: {appointment['id']}")
            
            # In real implementation:
            # service = build('calendar', 'v3', credentials=creds)
            # event = {
            #     'summary': f"Appointment with {appointment['doctor']}",
            #     'start': {'dateTime': f"{appointment['date']}T{appointment['time']}:00"},
            #     'end': {'dateTime': f"{appointment['date']}T{appointment['time']}:30"},
            #     'description': appointment['notes']
            # }
            # result = service.events().insert(calendarId='primary', body=event).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to Google Calendar: {e}")
            return False
    
    async def _get_patient_appointments(self, patient_name: str) -> List[Dict[str, Any]]:
        """Get upcoming appointments for a patient."""
        current_date = datetime.now().date()
        upcoming_appointments = []
        
        for appointment in self.appointments_db:
            if appointment["patient_name"] == patient_name and appointment["status"] == "scheduled":
                appointment_date = datetime.strptime(appointment["date"], "%Y-%m-%d").date()
                if appointment_date >= current_date:
                    upcoming_appointments.append(appointment)
        
        # Sort by date and time
        upcoming_appointments.sort(key=lambda x: f"{x['date']} {x['time']}")
        return upcoming_appointments
    
    async def _handle_reschedule_request(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle appointment reschedule request."""
        return {
            "status": "reschedule_requested",
            "message": "Reschedule functionality would be implemented here",
            "next_steps": ["Contact office to reschedule", "Check available times"]
        }
    
    async def _handle_cancel_request(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle appointment cancellation request."""
        return {
            "status": "cancel_requested",
            "message": "Cancellation functionality would be implemented here",
            "next_steps": ["Confirm cancellation", "Reschedule if needed"]
        }
    
    async def _handle_general_scheduling_query(self, message: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general scheduling queries."""
        return {
            "status": "general_info",
            "message": "General scheduling information provided",
            "available_services": [
                "Schedule follow-up appointments",
                "Check upcoming appointments",
                "Reschedule existing appointments",
                "Cancel appointments"
            ]
        }
    
    async def check_doctor_availability(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check availability for a specific doctor."""
        doctor = request.get("doctor", "Dr. Smith")
        days_ahead = request.get("days_ahead", 7)
        
        available_slots = await self._find_available_slots(doctor, days_ahead)
        
        return {
            "status": "success",
            "doctor": doctor,
            "available_slots": available_slots,
            "total_slots": len(available_slots)
        }
    
    async def schedule_appointment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a specific appointment."""
        doctor = request.get("doctor", "Dr. Smith")
        date = request.get("date")
        time = request.get("time")
        patient_context = request.get("patient_context", {})
        
        if not date or not time:
            return {
                "status": "error",
                "message": "Date and time are required"
            }
        
        slot = {"date": date, "time": time}
        appointment = await self._book_appointment(doctor, slot, patient_context)
        
        return {
            "status": "scheduled",
            "appointment": appointment
        }
    
    async def get_upcoming_appointments(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get upcoming appointments for a patient."""
        patient_context = request.get("patient_context", {})
        patient_name = patient_context.get("name", "Patient")
        
        appointments = await self._get_patient_appointments(patient_name)
        
        return {
            "status": "success",
            "appointments": appointments,
            "count": len(appointments)
        }
    
    async def cancel_appointment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an appointment."""
        appointment_id = request.get("appointment_id")
        
        if not appointment_id:
            return {
                "status": "error",
                "message": "Appointment ID is required"
            }
        
        # Find and cancel appointment
        for appointment in self.appointments_db:
            if appointment["id"] == appointment_id:
                appointment["status"] = "cancelled"
                return {
                    "status": "cancelled",
                    "appointment": appointment
                }
        
        return {
            "status": "not_found",
            "message": "Appointment not found"
        }
    
    async def reschedule_appointment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Reschedule an appointment."""
        appointment_id = request.get("appointment_id")
        new_date = request.get("new_date")
        new_time = request.get("new_time")
        
        if not all([appointment_id, new_date, new_time]):
            return {
                "status": "error",
                "message": "Appointment ID, new date, and new time are required"
            }
        
        # Find appointment and reschedule
        for appointment in self.appointments_db:
            if appointment["id"] == appointment_id:
                old_date = appointment["date"]
                old_time = appointment["time"]
                
                appointment["date"] = new_date
                appointment["time"] = new_time
                
                return {
                    "status": "rescheduled",
                    "appointment": appointment,
                    "old_datetime": f"{old_date} {old_time}",
                    "new_datetime": f"{new_date} {new_time}"
                }
        
        return {
            "status": "not_found",
            "message": "Appointment not found"
        }


# A2A Protocol handler for external calls
class SchedulerAgentA2AHandler:
    """Handler for A2A protocol calls to the Scheduler Agent."""
    
    def __init__(self):
        self.agent = SchedulerAgent()
    
    async def manage_appointments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A call for appointment management."""
        return await self.agent.manage_appointments(params)
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for A2A discovery."""
        return {
            "agent_name": "scheduler_agent",
            "agent_type": "CustomAgent",
            "capabilities": [
                {
                    "method": "manage_appointments",
                    "description": "Manage patient appointments and scheduling",
                    "parameters": {
                        "patient_message": "string",
                        "patient_context": "object"
                    },
                    "returns": "scheduling_result_object"
                },
                {
                    "method": "check_availability",
                    "description": "Check doctor availability",
                    "parameters": {
                        "doctor": "string",
                        "days_ahead": "integer"
                    },
                    "returns": "availability_object"
                }
            ],
            "specialization": "Appointment scheduling and calendar management",
            "integrations": ["Google Calendar API"],
            "version": "1.0.0"
        }