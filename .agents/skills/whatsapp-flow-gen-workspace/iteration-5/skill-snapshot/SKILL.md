---
name: whatsapp-flow-gen
description: Generate WhatsApp Flow JSON and its corresponding backend (defaulting to Python). Use this whenever a user wants to build interactive, form-based WhatsApp experiences, handle flow-related data exchange, or process final flow submissions via a webhook.
---

# WhatsApp Flow Generator

A specialized skill for building WhatsApp Flow packages consisting of the UI (JSON) and the Backend logic (Flow Endpoint + Webhook).

## When to use
- The user wants to build a "WhatsApp Flow".
- The user needs a `flow.json` file.
- The user needs a backend to handle both the Flow Endpoint (encrypted transitions) and the standard Webhook (receiving final data).

## Key Components

### 1. Flow JSON (`flow.json`)
Generate a valid UI schema for WhatsApp.
- Define screens, input fields, and routing.
- Use `data_exchange` for intermediate transitions.
- Use `complete` for the final submission.

#### ⚠️ CRITICAL RULES FOR DATA EXCHANGE
Every single `data_exchange` action **MUST** follow these rules to ensure the backend can identify the intent:
1. **Mandatory Payload Attribute**: You MUST include a unique attribute named `data_exchange_trigger` in the `payload` object.
2. **Descriptive Naming**: The value of `data_exchange_trigger` MUST be a descriptive string (e.g., `"validate_zip_code"`, `"fetch_available_seats"`, `"calculate_price"`).
3. **Consistency**: The backend generated MUST explicitly check this `data_exchange_trigger` value to route the logic.

**Example Payload Structure:**
```json
"on-click-action": {
  "name": "data_exchange",
  "payload": {
    "data_exchange_trigger": "fetch_product_details",
    "product_id": "${form.product_id}"
  }
}
```


### 2. Backend Logic (Decoupled & Comprehensive)
Generate a functional backend that handles the entire Flow lifecycle.

#### A. Flow Endpoint (`/whatsapp-flow`)
- **Action Handling**: `ping` and `data_exchange`.
- **Decoupled Security**: Uses `decrypt_payload(body)` and `encrypt_payload(response)`.
- **Response Format**: Base64 string with `Content-Type: text/plain`.

#### B. Standard Webhook (`/webhook`)
- **Action Handling**: Process incoming messages from WhatsApp.
- **Flow Response**: Specifically handle `interactive` messages of type `nfm_reply`.
- **Submission Function**: Generate a `handle_submission(flow_data)` function that processes the final JSON response received from the flow.

## Workflow
1. **Define Flow**: Identify screens and the final submission data.
2. **Generate JSON**: Create the `flow.json`.
3. **Generate Backend**: Create a Python file with TWO main endpoints:
    - `/whatsapp-flow`: For encrypted intermediate logic.
    - `/webhook`: For receiving the final `complete` result.
4. **Logic**: Ensure the `handle_submission` function is clearly defined to process the results.

## Implementation Details
- Default to **FastAPI**.
- Ensure the code is modular, separating the security layer from the business logic.
