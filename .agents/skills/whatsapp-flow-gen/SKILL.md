---
name: whatsapp-flow-gen
description: Generate WhatsApp Flow JSON and its corresponding backend (defaulting to Python). Use this whenever a user wants to build interactive, form-based WhatsApp experiences, handle flow-related data exchange, or process final flow submissions via a webhook.
---

# WhatsApp Flow Generator (STRICT DATA EXCHANGE)

This skill provides expert guidance for building valid WhatsApp Flow JSON and its corresponding backend logic.

### 🚨 NON-NEGOTIABLE MANDATES (YOUR TASK FAILS IF THESE ARE MISSED)

#### 1. Top-Level `flow.json` Requirements
Every `flow.json` MUST include these exact properties at the top level:
- [ ] `"version": "7.1"` (or latest)
- [ ] `"data_api_version": "3.0"` (MANDATORY for all flows)
- [ ] `"routing_model": { ... }` (MANDATORY to define transitions)

#### 2. Every Flow MUST End with a Terminal Screen
- [ ] Every user path MUST lead to a screen marked as `"terminal": true`.
- [ ] Every terminal screen MUST include a `Footer` component with a `complete` action.

#### 3. Backend Error Handling Pattern
The `/whatsapp-flow` endpoint MUST use this exact pattern:
```python
import traceback
from fastapi.responses import PlainTextResponse

@app.post("/whatsapp-flow")
async def handle_flow(request: Request):
    try:
        # ... logic ...
    except Exception as e:
        traceback.print_exc() # MANDATORY
        response = {
            "screen": decrypted_data.get('screen', '') if 'decrypted_data' in locals() else '',
            "data": {
                "error": True, # MANDATORY
                "error_message": str(e) # MANDATORY: ACTUAL REASON
            }
        }
        print("sending", response)
        # return encrypted response
```

#### 4. Terms and Conditions
- [ ] For agreements, you **MUST** use the `OptIn` component.
- [ ] Use `on-click-action` with `open_url` for the link.

### 🚨 CRITICAL PITFALLS TO AVOID
- **Expression Syntax**:
  - ❌ **NEVER** use `null`. Use `''` (empty string) or boolean checks.
  - ✅ **ALWAYS** use explicit comparisons in backticks: `` "`${data.field} == false`" ``.
- **TextInput Properties**: 
  - ❌ **NEVER** use `value`. ✅ **ALWAYS** use `init-value`.
  - ❌ **NEVER** use `error-text`. ✅ **ALWAYS** use `error-message`.
- **Selection Component Actions**: 
  - ❌ **NEVER** use `on-change-action`. ✅ **ALWAYS** use `on-select-action`.
- **Property Types**:
  - Properties like `visible`, `required`, and `enabled` MUST be literal booleans or backticked expressions.

### 🚨 STOP! YOU MUST INCLUDE `data_exchange_trigger` 🚨
Every `data_exchange` action you generate **MUST** include a key named `data_exchange_trigger` in its payload. If you omit this, the task is a FAILURE.

---

## Instructions
- Generate `flow.json` and a Python FastAPI backend.
- Backend must handle `/whatsapp-flow` (encrypted intermediate logic) and `/webhook` (receiving final results).
- The `/whatsapp-flow` endpoint processes `ping` and `data_exchange`.
- The `/webhook` endpoint processes `interactive` messages of type `nfm_reply`.
- Always generate a `handle_submission(flow_data)` function.
- **Strictly adhere to version limits** defined in `references/rules.md` (e.g., v7.1 for latest features).
