"""
Quick test to reproduce the HTTP 500 error when calling /api/resume
"""
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from graph import graph
from state import initial_state
import uuid

# Simulate first invoke (generate)
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

state = initial_state(
    raw_jd="Senior ML Engineer at Stripe... (truncated for testing)",
    raw_resume="Alex Rivera — ML Engineer...(truncated for testing)",
    recipient_type="recruiter",
)

print("=" * 80)
print(f"Testing graph with thread_id: {thread_id}")
print("=" * 80)

try:
    print("\n[1] Running first invoke (should interrupt before export_node)...")
    result = graph.invoke(state, config=config)
    print("✓ First invoke completed")
    print(f"  Generated emails: {len(result.get('generated_emails', []))}")
    print(f"  Subject lines: {len(result.get('subject_lines', []))}")
    print(f"  State keys: {list(result.keys())}")
except Exception as e:
    print(f"✗ First invoke failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Simulate second invoke (resume)
try:
    print("\n[2] Running second invoke (resume with user_edits)...")
    user_edits = [{
        "recipient_type": "recruiter",
        "edited_body": "Edited email body here",
        "edited_subject": "Edited subject",
        "reset_to_ai": False,
    }]
    
    final = graph.invoke({"user_edits": user_edits}, config=config)
    print("✓ Second invoke completed")
    print(f"  Outreach status: {final.get('outreach_status')}")
    print(f"  Generated emails: {len(final.get('generated_emails', []))}")
    print(f"  State keys: {list(final.keys())}")
except Exception as e:
    print(f"✗ Second invoke failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ All tests passed!")
print("=" * 80)
