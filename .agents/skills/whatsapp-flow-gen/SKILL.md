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
- `"data_api_version": "3.0"`
- `"routing_model": { ... }` (defining the valid screen transitions)

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

### 🚨 STOP! YOU MUST INCLUDE `data_exchange_trigger` 🚨

Every `data_exchange` action you generate **MUST** include a key named `data_exchange_trigger` in its payload. If you omit this, the task is a FAILURE.

#### 1. REQUIRED JSON PATTERN (`flow.json`)
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
