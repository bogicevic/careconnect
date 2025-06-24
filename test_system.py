#!/usr/bin/env python3
"""
Test script for CareConnect Multi-Agent System
Run this to verify the system is working properly before using `adk web`
"""

import asyncio
import sys
import os

# Add agent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

try:
    from agent.agent import CareConnectAgent
    print("✅ Successfully imported CareConnectAgent")
except ImportError as e:
    print(f"❌ Failed to import CareConnectAgent: {e}")
    sys.exit(1)


async def test_basic_functionality():
    """Test basic agent functionality."""
    print("\n🧪 Testing CareConnect System...")
    
    # Initialize the agent
    try:
        agent = CareConnectAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False
    
    # Test messages
    test_messages = [
        "Hello, I'm Elena. How are you today?",
        "I'm feeling pretty good, thank you. A little sore, but better than yesterday.",
        "When should I take my pain medication?",
        "I have a high fever and my incision site is red and hot.",
        "When is my next appointment with Dr. Smith?"
    ]
    
    print("\n📝 Testing conversation scenarios...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        print(f"Patient: {message}")
        
        try:
            response = await agent.process_message(message)
            print(f"CareConnect: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("✅ Response generated successfully")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return False
    
    # Test system status
    print("\n📊 Testing system status...")
    try:
        status = await agent.get_system_status()
        print(f"✅ System status: {status}")
    except Exception as e:
        print(f"❌ Error getting system status: {e}")
        return False
    
    # Cleanup
    try:
        await agent.shutdown()
        print("✅ Agent shutdown successfully")
    except Exception as e:
        print(f"⚠️ Warning during shutdown: {e}")
    
    return True


async def test_individual_agents():
    """Test individual agent components."""
    print("\n🔧 Testing individual agent components...")
    
    try:
        from agent.triage_agent import TriageAgentA2AHandler
        from agent.scheduler_agent import SchedulerAgentA2AHandler
        from agent.pharmacy_agent import PharmacyAgentA2AHandler
        from agent.nurse_notifier_agent import NurseNotifierAgentA2AHandler
        
        print("✅ All agent imports successful")
        
        # Test Triage Agent
        print("\n🏥 Testing Triage Agent...")
        triage_handler = TriageAgentA2AHandler()
        triage_result = await triage_handler.assess_symptoms({
            "patient_message": "I have a high fever and my incision is red",
            "patient_context": {"name": "Elena", "condition": "post-operative knee replacement"}
        })
        print(f"✅ Triage assessment: {triage_result.get('risk_level', 'Unknown')}")
        
        # Test Scheduler Agent
        print("\n📅 Testing Scheduler Agent...")
        scheduler_handler = SchedulerAgentA2AHandler()
        scheduler_result = await scheduler_handler.manage_appointments({
            "patient_message": "I need to schedule a follow-up appointment",
            "patient_context": {"name": "Elena"}
        })
        print(f"✅ Scheduler result: {scheduler_result.get('status', 'Unknown')}")
        
        # Test Pharmacy Agent
        print("\n💊 Testing Pharmacy Agent...")
        pharmacy_handler = PharmacyAgentA2AHandler()
        pharmacy_result = await pharmacy_handler.manage_medications({
            "patient_message": "When should I take my medication?",
            "patient_context": {"name": "Elena"}
        })
        print(f"✅ Pharmacy result: {pharmacy_result.get('status', 'Unknown')}")
        
        # Test Nurse Notifier Agent
        print("\n🚨 Testing Nurse Notifier Agent...")
        notifier_handler = NurseNotifierAgentA2AHandler()
        notifier_result = await notifier_handler.send_alert({
            "patient_message": "I have a high fever",
            "triage_assessment": {"risk_level": "CRITICAL", "escalate": True},
            "patient_context": {"name": "Elena"},
            "priority": "URGENT"
        })
        print(f"✅ Notification result: {notifier_result.get('status', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing individual agents: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'adk',
        'adk.agents',
        'adk.models'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_modules)}")
        print("Please install the Google ADK and required dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    return True


async def main():
    """Main test function."""
    print("🚀 CareConnect System Test Suite")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Test basic functionality
    basic_test_passed = await test_basic_functionality()
    
    # Test individual agents
    agent_test_passed = await test_individual_agents()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"Basic functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"Individual agents: {'✅ PASSED' if agent_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and agent_test_passed:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run 'adk web' to start the web interface")
        print("2. Run 'adk run agent' to use the CLI interface")
        print("3. Or run 'python agent/agent.py' for direct testing")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)