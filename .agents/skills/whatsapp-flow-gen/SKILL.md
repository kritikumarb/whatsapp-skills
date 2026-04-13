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
- **TextInput Properties**: 
  - ❌ **NEVER** use `value`. ✅ **ALWAYS** use `init-value` for pre-populating.
  - ❌ **NEVER** use `error-text`. ✅ **ALWAYS** use `error-message` for validation errors.
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

### 🚨 MANDATORY: Backend Error Handling & UI Popups
When you return a response with `"error": true`, WhatsApp will **automatically show a native error popup** to the user. 

- **Reserved Keywords**: `error` and `error_message` are **inbuilt keywords**. 
- **NO `flow.json` Declaration**: You **MUST NOT** declare `error` or `error_message` in the `data` block of any screen in `flow.json`.
- **NO Manual Error UI**: Do not create `TextBody` or other components to display these errors; the native popup handles this automatically.

#### 1. Technical Error (Global Catch)
Every `/whatsapp-flow` intermediate logic MUST be wrapped in a `try-except` block:
```python
except Exception as e:
    traceback.print_exc()
    response = {
        "screen": decrypted_data.get('screen', ''),
        "data": {
            "error": True,
            "error_message": str(e) # Triggers native UI popup
        }
    }
    # ... encrypt and return ...
```

#### 2. Business Validation (Trigger Level)
Use the same format to prevent navigation and show a message if a user's selection is invalid:
```python
if trigger == "check_availability":
    if not is_available:
        return {
            "screen": "CURRENT_SCREEN_ID", # Keep user on same screen
            "data": {
                "error": True,
                "error_message": "This date is fully booked. Please choose another."
            }
        }
```

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
