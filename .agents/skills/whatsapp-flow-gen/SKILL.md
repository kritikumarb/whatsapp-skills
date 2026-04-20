---
name: whatsapp-flow-gen
description: Expert system for generating WhatsApp Flow JSON (v7.1+) and Python/FastAPI backends. This skill contains HARD CONSTRAINTS and a MANDATORY validation script. Use this skill whenever a user wants to build any WhatsApp Flow. Even if they ask for a "simple flow", you MUST use the validation script and refuse invalid requests.
---

# WhatsApp Flow Generator (STRICT DATA EXCHANGE)

This skill provides expert guidance and valid JSON generation for WhatsApp Flows. It enforces strict compliance with Meta's component limits and property rules.

### 🛑 CRITICAL: MANDATORY VALIDATION SCRIPT 🛑
After generating your `flow.json`, you **MUST** run the validation script:
```bash
python scripts/validate_flow.py path/to/your/flow.json
```
If this script returns ANY error, you **MUST** fix the JSON and rerun the validation until it passes. **NEVER** present unvalidated JSON to the user.

### 🚨 PRE-FLIGHT CHECKLIST (DO NOT EMIT JSON UNLESS ALL PASS)
1. **Character Counts**: Have you MANUALLY counted the characters for all `TextHeading` (max 80), `TextSubheading` (max 80), and `TextInput` labels (max 20)? **Truncate immediately if they exceed limits.**
2. **Footer Symmetry**: If a `Footer` is inside an `If`, it **MUST** exist in both `then` and `else` branches. If the user asks for it in only one branch, you **MUST** explain the rule and add it to both or move it outside the `If`.
3. **Exclusivity**: `PhotoPicker` and `DocumentPicker` **CANNOT** coexist on the same screen. Split them into two screens.
4. **Isolation**: `NavigationList` **MUST** be the only component on its screen.
5. **Terminal Screen**: Every Flow path **MUST** end in a screen with `terminal: true` and a `Footer` with a `complete` action.

### 🚨 MANDATORY: CHARACTER COUNTING (HARD BOUNDARIES)
You MUST treat character limits as hard physical boundaries. 
- `TextHeading`: 80 chars.
- `TextSubheading`: 80 chars.
- `TextInput label`: 20 chars.
- `Footer label`: 35 chars.
If the user's requested text exceeds these, you **MUST** truncate it or reformulate it to fit. **NEVER** emit text that exceeds these limits, even if the user says "exactly".

### 🚨 Component Validation (Source of Truth)
Before emitting ANY component JSON, you **MUST** consult `references/component-rules.md`. This file contains the mandatory limits (character counts, counts per screen, exclusivity) for every component.
- ❌ **REFUSE** to emit JSON that violates these rules.
- ✅ **ALWAYS** check `SECTION 2 — CROSS-COMPONENT EXCLUSIVITY RULES` for screen-level conflicts.

---

#### 1. Top-Level `flow.json` Requirements
Every `flow.json` MUST include these exact properties at the top level:
- [ ] `"version": "7.1"`
- [ ] `"data_api_version": "3.0"`
- [ ] `"routing_model": { ... }`

#### 2. Backend Error Handling Pattern
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

### 🚨 STOP! YOU MUST INCLUDE `data_exchange_trigger` 🚨
Every `data_exchange` action you generate **MUST** include a key named `data_exchange_trigger` in its payload. If you omit this, the task is a FAILURE.

---

## Instructions
- Generate `flow.json` and a Python FastAPI backend.
- **Run `scripts/validate_flow.py` on your output.**
- Backend must handle `/whatsapp-flow` (intermediate) and `/webhook` (final).
- Always generate a `handle_submission(flow_data)` function.
- **Strictly adhere to version limits** defined in `references/rules.md` and `references/component-rules.md`.
