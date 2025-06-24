"""Nurse Notifier Agent - Alert notification specialist for CareConnect system."""

from adk.agents import CustomAgent
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class NurseNotifierAgent(CustomAgent):
    """
    The Nurse-Notifier-Agent specializes in sending urgent alerts to healthcare providers
    when patients report concerning symptoms or require immediate attention.
    """
    
    def __init__(self, name: str = "nurse_notifier_agent"):
        super().__init__(name=name)
        
        # Mock nurse/healthcare provider database
        self.healthcare_providers = self._initialize_healthcare_providers()
        
        # Alert configuration
        self.alert_config = {
            "urgent_response_time_minutes": 15,
            "high_response_time_minutes": 60,
            "normal_response_time_minutes": 240,
            "escalation_levels": ["URGENT", "HIGH", "NORMAL"],
            "notification_channels": ["dashboard", "sms", "email", "pager"]
        }
        
        # Alert history for tracking and auditing
        self.alert_history = []
    
    def _initialize_healthcare_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mock healthcare provider database."""
        return {
            "nurse_david": {
                "name": "David Johnson",
                "role": "Registered Nurse",
                "department": "Orthopedic Floor",
                "contact": {
                    "phone": "+1-555-0123",
                    "email": "david.johnson@hospital.com",
                    "pager": "555-1234",
                    "dashboard_id": "nurse_dashboard_001"
                },
                "shift_schedule": {
                    "monday": "07:00-19:00",
                    "tuesday": "07:00-19:00",
                    "wednesday": "07:00-19:00",
                    "thursday": "off",
                    "friday": "off",
                    "saturday": "07:00-19:00",
                    "sunday": "07:00-19:00"
                },
                "specializations": ["post-operative care", "orthopedic patients"],
                "on_call": True
            },
            "dr_smith": {
                "name": "Dr. Sarah Smith",
                "role": "Orthopedic Surgeon",
                "department": "Orthopedic Surgery",
                "contact": {
                    "phone": "+1-555-0456",
                    "email": "sarah.smith@hospital.com",
                    "pager": "555-5678",
                    "dashboard_id": "doctor_dashboard_002"
                },
                "shift_schedule": {
                    "monday": "08:00-17:00",
                    "tuesday": "08:00-17:00",
                    "wednesday": "08:00-17:00",
                    "thursday": "08:00-17:00",
                    "friday": "08:00-17:00",
                    "saturday": "on-call",
                    "sunday": "off"
                },
                "specializations": ["knee replacement", "hip replacement", "joint surgery"],
                "on_call": False
            }
        }
    
    async def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the Nurse Notifier Agent.
        Handles various alert and notification requests.
        """
        try:
            action = request.get("action", "send_alert")
            
            if action == "send_alert":
                return await self.send_alert(request)
            elif action == "get_alert_history":
                return await self.get_alert_history(request)
            elif action == "update_provider_status":
                return await self.update_provider_status(request)
            elif action == "check_provider_availability":
                return await self.check_provider_availability(request)
            elif action == "escalate_alert":
                return await self.escalate_alert(request)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "available_actions": [
                        "send_alert", "get_alert_history", "update_provider_status",
                        "check_provider_availability", "escalate_alert"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error in NurseNotifierAgent.invoke: {e}")
            return {
                "status": "error",
                "message": f"Nurse notifier agent error: {str(e)}"
            }
    
    async def send_alert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send alert to healthcare providers based on triage assessment.
        This is the main method called by the Triage-Agent.
        """
        try:
            patient_message = request.get("patient_message", "")
            triage_assessment = request.get("triage_assessment", {})
            patient_context = request.get("patient_context", {})
            priority = request.get("priority", "HIGH")
            timestamp = request.get("timestamp", datetime.now().isoformat())
            
            logger.info(f"Sending {priority} alert for patient: {patient_context.get('name', 'Unknown')}")
            
            # Create alert object
            alert = await self._create_alert(
                patient_message, triage_assessment, patient_context, priority, timestamp
            )
            
            # Determine which healthcare providers to notify
            providers_to_notify = await self._determine_notification_recipients(alert)
            
            # Send notifications via multiple channels
            notification_results = []
            for provider_id in providers_to_notify:
                provider = self.healthcare_providers.get(provider_id)
                if provider:
                    result = await self._send_notification_to_provider(alert, provider)
                    notification_results.append(result)
            
            # Store alert in history
            self.alert_history.append(alert)
            
            # Log the alert for auditing
            await self._log_alert_for_audit(alert, notification_results)
            
            return {
                "status": "alert_sent",
                "alert_id": alert["alert_id"],
                "priority": priority,
                "providers_notified": len(notification_results),
                "notification_results": notification_results,
                "expected_response_time_minutes": self._get_expected_response_time(priority),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return {
                "status": "error",
                "message": "Failed to send alert",
                "error_details": str(e)
            }
    
    async def _create_alert(self, patient_message: str, triage_assessment: Dict[str, Any], 
                           patient_context: Dict[str, Any], priority: str, timestamp: str) -> Dict[str, Any]:
        """Create a structured alert object."""
        
        alert_id = f"ALERT_{len(self.alert_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract key information for the alert
        patient_name = patient_context.get("name", "Unknown Patient")
        symptoms = triage_assessment.get("symptoms_identified", [])
        risk_level = triage_assessment.get("risk_level", "MODERATE")
        urgency_score = triage_assessment.get("urgency_score", 5)
        
        # Create concise alert message
        alert_message = await self._format_alert_message(
            patient_name, patient_message, symptoms, risk_level
        )
        
        alert = {
            "alert_id": alert_id,
            "timestamp": timestamp,
            "priority": priority,
            "risk_level": risk_level,
            "urgency_score": urgency_score,
            "patient_info": {
                "name": patient_name,
                "condition": patient_context.get("condition", "Unknown"),
                "original_message": patient_message
            },
            "triage_assessment": triage_assessment,
            "alert_message": alert_message,
            "status": "sent",
            "response_required": True,
            "escalation_level": 0,
            "created_by": "triage_agent"
        }
        
        return alert
    
    async def _format_alert_message(self, patient_name: str, patient_message: str, 
                                   symptoms: List[str], risk_level: str) -> str:
        """Format a concise, actionable alert message for healthcare providers."""
        
        # Create urgency indicator
        urgency_indicator = {
            "CRITICAL": "🚨 URGENT",
            "MODERATE": "⚠️ HIGH PRIORITY",
            "LOW": "ℹ️ ROUTINE"
        }.get(risk_level, "⚠️ ATTENTION")
        
        # Format symptoms list
        symptoms_text = ", ".join(symptoms) if symptoms else "See details"
        
        # Create concise alert
        alert_message = f"""
{urgency_indicator}: Patient Alert - {patient_name}

SYMPTOMS: {symptoms_text}
PATIENT REPORT: "{patient_message[:150]}{'...' if len(patient_message) > 150 else ''}"

RISK LEVEL: {risk_level}
IMMEDIATE ACTION: {"Contact patient immediately" if risk_level == "CRITICAL" else "Review and respond within expected timeframe"}

Alert ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}
        """.strip()
        
        return alert_message
    
    async def _determine_notification_recipients(self, alert: Dict[str, Any]) -> List[str]:
        """Determine which healthcare providers should receive the alert."""
        
        priority = alert["priority"]
        risk_level = alert["risk_level"]
        
        recipients = []
        
        # Always notify the primary nurse
        recipients.append("nurse_david")
        
        # For critical alerts, also notify the doctor
        if risk_level == "CRITICAL" or priority == "URGENT":
            recipients.append("dr_smith")
        
        # Filter based on availability (simplified check)
        available_recipients = []
        for recipient_id in recipients:
            provider = self.healthcare_providers.get(recipient_id)
            if provider and provider.get("on_call", False):
                available_recipients.append(recipient_id)
        
        # If no one is available, escalate to all providers
        if not available_recipients:
            available_recipients = list(self.healthcare_providers.keys())
        
        return available_recipients
    
    async def _send_notification_to_provider(self, alert: Dict[str, Any], provider: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification to a specific healthcare provider via multiple channels."""
        
        provider_name = provider["name"]
        contact_info = provider["contact"]
        priority = alert["priority"]
        
        notification_result = {
            "provider_name": provider_name,
            "provider_role": provider["role"],
            "channels_used": [],
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Send to dashboard (always)
            dashboard_result = await self._send_dashboard_notification(alert, contact_info["dashboard_id"])
            notification_result["channels_used"].append("dashboard")
            
            # For urgent alerts, use additional channels
            if priority in ["URGENT", "HIGH"]:
                # Send SMS
                sms_result = await self._send_sms_notification(alert, contact_info["phone"])
                notification_result["channels_used"].append("sms")
                
                # Send to pager for critical alerts
                if priority == "URGENT":
                    pager_result = await self._send_pager_notification(alert, contact_info["pager"])
                    notification_result["channels_used"].append("pager")
            
            # Always send email for record keeping
            email_result = await self._send_email_notification(alert, contact_info["email"])
            notification_result["channels_used"].append("email")
            
            logger.info(f"Notification sent to {provider_name} via {len(notification_result['channels_used'])} channels")
            
        except Exception as e:
            logger.error(f"Error sending notification to {provider_name}: {e}")
            notification_result["status"] = "error"
            notification_result["error"] = str(e)
        
        return notification_result
    
    async def _send_dashboard_notification(self, alert: Dict[str, Any], dashboard_id: str) -> bool:
        """Send notification to healthcare provider dashboard (mock implementation)."""
        try:
            logger.info(f"Sending dashboard notification to {dashboard_id}")
            
            # Mock dashboard API call
            dashboard_payload = {
                "alert_id": alert["alert_id"],
                "priority": alert["priority"],
                "message": alert["alert_message"],
                "patient_name": alert["patient_info"]["name"],
                "timestamp": alert["timestamp"],
                "requires_response": alert["response_required"]
            }
            
            # In real implementation:
            # response = requests.post(f"https://dashboard-api.hospital.com/alerts/{dashboard_id}", 
            #                         json=dashboard_payload, headers=auth_headers)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending dashboard notification: {e}")
            return False
    
    async def _send_sms_notification(self, alert: Dict[str, Any], phone_number: str) -> bool:
        """Send SMS notification via Twilio (mock implementation)."""
        try:
            logger.info(f"Sending SMS notification to {phone_number}")
            
            # Create concise SMS message
            sms_message = f"""
PATIENT ALERT: {alert['patient_info']['name']}
Priority: {alert['priority']}
Symptoms: {', '.join(alert['triage_assessment'].get('symptoms_identified', [])[:2])}
Check dashboard for full details.
Alert ID: {alert['alert_id']}
            """.strip()
            
            # Mock Twilio API call
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # message = client.messages.create(
            #     body=sms_message,
            #     from_='+1234567890',
            #     to=phone_number
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return False
    
    async def _send_pager_notification(self, alert: Dict[str, Any], pager_number: str) -> bool:
        """Send pager notification (mock implementation)."""
        try:
            logger.info(f"Sending pager notification to {pager_number}")
            
            # Mock pager system call
            pager_message = f"URGENT: {alert['patient_info']['name']} - {alert['alert_id']}"
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending pager notification: {e}")
            return False
    
    async def _send_email_notification(self, alert: Dict[str, Any], email_address: str) -> bool:
        """Send email notification (mock implementation)."""
        try:
            logger.info(f"Sending email notification to {email_address}")
            
            # Create detailed email content
            email_subject = f"Patient Alert - {alert['priority']} - {alert['patient_info']['name']}"
            email_body = f"""
Healthcare Provider Alert

Alert ID: {alert['alert_id']}
Timestamp: {alert['timestamp']}
Priority: {alert['priority']}
Risk Level: {alert['risk_level']}

Patient Information:
- Name: {alert['patient_info']['name']}
- Condition: {alert['patient_info']['condition']}

Patient Report:
"{alert['patient_info']['original_message']}"

Triage Assessment:
- Symptoms Identified: {', '.join(alert['triage_assessment'].get('symptoms_identified', []))}
- Reasoning: {alert['triage_assessment'].get('reasoning', 'N/A')}
- Recommendations: {', '.join(alert['triage_assessment'].get('recommendations', []))}

Please respond according to your facility's protocols.

This is an automated alert from the CareConnect system.
            """
            
            # Mock email sending (would use SendGrid, AWS SES, etc.)
            # import sendgrid
            # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            # message = Mail(from_email='alerts@careconnect.com', to_emails=email_address,
            #               subject=email_subject, html_content=email_body)
            # response = sg.send(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def _log_alert_for_audit(self, alert: Dict[str, Any], notification_results: List[Dict[str, Any]]):
        """Log alert for auditing and compliance (mock implementation)."""
        try:
            audit_log = {
                "alert_id": alert["alert_id"],
                "timestamp": alert["timestamp"],
                "patient_name": alert["patient_info"]["name"],
                "priority": alert["priority"],
                "risk_level": alert["risk_level"],
                "providers_notified": [r["provider_name"] for r in notification_results],
                "notification_channels": [channel for r in notification_results for channel in r["channels_used"]],
                "triage_assessment": alert["triage_assessment"],
                "system_version": "1.0.0"
            }
            
            # In real implementation, this would go to Google Cloud Pub/Sub -> BigQuery
            logger.info(f"Audit log created for alert {alert['alert_id']}")
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
    
    def _get_expected_response_time(self, priority: str) -> int:
        """Get expected response time in minutes based on priority."""
        return {
            "URGENT": self.alert_config["urgent_response_time_minutes"],
            "HIGH": self.alert_config["high_response_time_minutes"],
            "NORMAL": self.alert_config["normal_response_time_minutes"]
        }.get(priority, self.alert_config["high_response_time_minutes"])
    
    async def get_alert_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get alert history for auditing and analysis."""
        try:
            limit = request.get("limit", 50)
            patient_name = request.get("patient_name")
            
            filtered_alerts = self.alert_history
            
            if patient_name:
                filtered_alerts = [
                    alert for alert in self.alert_history 
                    if alert["patient_info"]["name"] == patient_name
                ]
            
            # Sort by timestamp (most recent first)
            filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return {
                "status": "success",
                "alerts": filtered_alerts[:limit],
                "total_alerts": len(filtered_alerts),
                "limit_applied": limit
            }
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return {
                "status": "error",
                "message": "Unable to retrieve alert history",
                "error_details": str(e)
            }
    
    async def update_provider_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update healthcare provider availability status."""
        try:
            provider_id = request.get("provider_id")
            on_call = request.get("on_call")
            
            if provider_id in self.healthcare_providers:
                self.healthcare_providers[provider_id]["on_call"] = on_call
                return {
                    "status": "updated",
                    "provider_id": provider_id,
                    "on_call": on_call
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Provider {provider_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Error updating provider status: {e}")
            return {
                "status": "error",
                "message": "Unable to update provider status",
                "error_details": str(e)
            }
    
    async def check_provider_availability(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Check which healthcare providers are currently available."""
        try:
            available_providers = []
            
            for provider_id, provider in self.healthcare_providers.items():
                if provider.get("on_call", False):
                    available_providers.append({
                        "provider_id": provider_id,
                        "name": provider["name"],
                        "role": provider["role"],
                        "department": provider["department"]
                    })
            
            return {
                "status": "success",
                "available_providers": available_providers,
                "total_available": len(available_providers)
            }
            
        except Exception as e:
            logger.error(f"Error checking provider availability: {e}")
            return {
                "status": "error",
                "message": "Unable to check provider availability",
                "error_details": str(e)
            }
    
    async def escalate_alert(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate an existing alert to higher priority."""
        try:
            alert_id = request.get("alert_id")
            new_priority = request.get("new_priority", "URGENT")
            
            # Find the alert
            for alert in self.alert_history:
                if alert["alert_id"] == alert_id:
                    old_priority = alert["priority"]
                    alert["priority"] = new_priority
                    alert["escalation_level"] += 1
                    
                    # Send escalated notification
                    escalation_result = await self.send_alert({
                        "patient_message": f"ESCALATED: {alert['patient_info']['original_message']}",
                        "triage_assessment": alert["triage_assessment"],
                        "patient_context": alert["patient_info"],
                        "priority": new_priority,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return {
                        "status": "escalated",
                        "alert_id": alert_id,
                        "old_priority": old_priority,
                        "new_priority": new_priority,
                        "escalation_level": alert["escalation_level"],
                        "escalation_result": escalation_result
                    }
            
            return {
                "status": "not_found",
                "message": f"Alert {alert_id} not found"
            }
            
        except Exception as e:
            logger.error(f"Error escalating alert: {e}")
            return {
                "status": "error",
                "message": "Unable to escalate alert",
                "error_details": str(e)
            }


# A2A Protocol handler for external calls
class NurseNotifierAgentA2AHandler:
    """Handler for A2A protocol calls to the Nurse Notifier Agent."""
    
    def __init__(self):
        self.agent = NurseNotifierAgent()
    
    async def send_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A call for sending alerts."""
        return await self.agent.send_alert(params)
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities for A2A discovery."""
        return {
            "agent_name": "nurse_notifier_agent",
            "agent_type": "CustomAgent",
            "capabilities": [
                {
                    "method": "send_alert",
                    "description": "Send urgent alerts to healthcare providers",
                    "parameters": {
                        "patient_message": "string",
                        "triage_assessment": "object",
                        "patient_context": "object",
                        "priority": "string",
                        "timestamp": "string"
                    },
                    "returns": "alert_result_object"
                },
                {
                    "method": "get_alert_history",
                    "description": "Get alert history for auditing",
                    "parameters": {
                        "limit": "integer",
                        "patient_name": "string"
                    },
                    "returns": "alert_history_object"
                }
            ],
            "specialization": "Healthcare provider notifications and alerts",
            "integrations": ["Twilio SMS", "Email", "Pager Systems", "Dashboard APIs"],
            "version": "1.0.0"
        }