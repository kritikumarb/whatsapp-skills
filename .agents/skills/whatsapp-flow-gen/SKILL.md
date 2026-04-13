---
name: whatsapp-flow-gen
description: Generate WhatsApp Flow JSON and its corresponding backend (defaulting to Python). Use this whenever a user wants to build interactive, form-based WhatsApp experiences, handle flow-related data exchange, or process final flow submissions via a webhook.
---

# WhatsApp Flow Generator (STRICT DATA EXCHANGE)

This skill provides expert guidance for building valid WhatsApp Flow JSON and its corresponding backend logic.

### 🚨 MANDATORY: Every Flow MUST End with a Terminal Screen
You **MUST** ensure that every possible user path in the `flow.json` leads to a screen marked as `"terminal": true`. A terminal screen MUST include a `Footer` component with a `complete` action.

### 🚨 MANDATORY: Data Endpoint Configuration
If the flow uses a `data_exchange` action, you **MUST** include the following at the top-level of `flow.json`:
- `"data_api_version": "3.0"` (MANDATORY for all endpoint flows)
- `"routing_model": { ... }` (MANDATORY to define transitions)

```json
{
  "version": "7.1",
  "data_api_version": "3.0", // DO NOT FORGET THIS
  "routing_model": { ... },
  "screens": [ ... ]
}
```

### 🚨 MANDATORY: Terms and Conditions
For any user agreement, "Terms and Conditions", or "Privacy Policy", you **MUST** use the `OptIn` component.
- Use the `on-click-action` with `open_url` to provide the link to the full terms.
- Set `required: true` if the user must accept to proceed.

```json
{
  "type": "OptIn",
  "name": "terms_accepted",
  "label": "I agree to the Terms and Conditions",
  "required": true,
  "on-click-action": { 
    "name": "open_url", 
    "url": "https://example.com/terms" 
  }
}
```

### 🚨 CRITICAL PITFALLS TO AVOID (STRICT ENFORCEMENT)
- **Selection Component Actions**: Components that involve selecting a value (**DatePicker**, **CalendarPicker**, **Dropdown**, **CheckboxGroup**, **RadioButtonsGroup**, **ChipsSelector**) MUST use **`on-select-action`**.
  - ❌ **NEVER** use `on-change-action` (It is INVALID and will cause a crash).
  - ✅ **ALWAYS** use `on-select-action`.
- **Property Types (Booleans)**: Properties like **`visible`**, **`required`**, and **`enabled`** MUST be valid booleans.
  - **Direct Reference**: `"${data.field}"` is allowed ONLY if it's a direct reference to a boolean.
  - **Expressions/Logic**: If you use ANY operators (like `!`, `==`, `&&`), you **MUST** use backticks: `` "`!${data.field}`" ``.
  - ❌ **WRONG**: `"visible": "!${data.field}"` (This is a string).
  - ✅ **CORRECT**: `"visible": "`!${data.field}`"` (Backticks make it an expression).

#### REQUIRED TERMINAL SCREEN PATTERN
```json
{
  "id": "SUCCESS_SCREEN",
  "terminal": true,
  "layout": {
    "type": "SingleColumnLayout",
    "children": [
      { "type": "TextHeading", "text": "Confirmation" },
      { "type": "TextBody", "text": "Your request has been submitted successfully." },
      { 
        "type": "Footer", 
        "label": "Finish", 
        "on-click-action": { "name": "complete", "payload": {} } 
      }
    ]
  }
}
```

### 🚨 MANDATORY: Backend Error Handling
Every `/whatsapp-flow` intermediate logic MUST be wrapped in a `try-except` block. On any error, you MUST return a standardized error response containing the **actual error message**:

```python
import traceback
from fastapi.responses import PlainTextResponse

# Inside the /whatsapp-flow endpoint logic:
try:
    # ... decryption and trigger logic ...
except Exception as e:
    traceback.print_exc()
    # Use the screen ID from decrypted_data if available
    response = {
        "screen": decrypted_data.get('screen', ''),
        "data": {
            "error": True,
            "error_message": str(e) # ACTUAL ERROR REASON
        }
    }
    print("sending", response)
    encrypted_response = encrypt_response(response, aes_key, iv)
    return PlainTextResponse(content=encrypted_response, media_type='text/plain')
```

- **Per-Trigger Handling**: Every specific `data_exchange_trigger` block MUST also have internal error handling to ensure the flow never crashes silently.

### 🚨 STOP! YOU MUST INCLUDE `data_exchange_trigger` 🚨

Every `data_exchange` action you generate **MUST** include a key named `data_exchange_trigger` in its payload. If you omit this, the task is a FAILURE.

#### 1. REQUIRED JSON PATTERN (`flow.json`)
Every flow MUST include `data_api_version` and `version` at the top level.
```json
{
  "version": "7.1",
  "data_api_version": "3.0", // MANDATORY: YOUR TASK FAILS IF THIS IS MISSING
  "routing_model": {
    "SCREEN_A": ["SCREEN_B"],
    "SCREEN_B": []
  },
  "screens": [ ... ]
}
```

Every `data_exchange` action MUST follow this pattern:
```json
"on-click-action": {
  "name": "data_exchange",
  "payload": {
    "data_exchange_trigger": "DESCRIBE_YOUR_ACTION", // THIS IS MANDATORY
    "other_field": "${form.other_field}"
  }
}
```

#### 2. REQUIRED BACKEND PATTERN (`main.py`)
The backend MUST check for the trigger:
```python
elif action == "data_exchange":
    trigger = data.get("data_exchange_trigger") # THIS IS MANDATORY
    if trigger == "DESCRIBE_YOUR_ACTION":
        # logic...
```

---

## Instructions
- Generate `flow.json` and a Python FastAPI backend.
- Backend must handle `/whatsapp-flow` (encrypted intermediate logic) and `/webhook` (receiving final results).
- The `/whatsapp-flow` endpoint processes `ping` and `data_exchange`.
- The `/webhook` endpoint processes `interactive` messages of type `nfm_reply`.
- Always generate a `handle_submission(flow_data)` function.
- **Strictly adhere to version limits** defined in `references/rules.md` (e.g., v7.1 for latest features).
