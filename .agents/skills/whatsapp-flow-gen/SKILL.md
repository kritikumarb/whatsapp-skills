---
name: whatsapp-flow-gen
description: Generate WhatsApp Flow JSON and its corresponding backend (defaulting to Python). Use this whenever a user wants to build interactive, form-based WhatsApp experiences, handle flow-related data exchange, or process final flow submissions via a webhook.
---

# WhatsApp Flow Generator (STRICT DATA EXCHANGE)

This skill provides expert guidance for building valid WhatsApp Flow JSON and its corresponding backend logic.

### 🚨 MANDATORY: Consult Authoritative Rules
Before generating or modifying any Flow JSON, you **MUST** consult the authoritative rules located in:
`references/rules.md`

This file contains critical constraints for:
- **Routing Model**: Max 10 edges, entry/terminal rules.
- **Components**: Per-screen limits (max 50), version-specific availability, character limits.
- **Actions**: `navigate` vs `complete` vs `data_exchange` vs `update_data`.
- **Media**: PhotoPicker/DocumentPicker restrictions.
- **Data Binding**: `${data.*}`, `${form.*}`, and `${screen.*}` global references.

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
