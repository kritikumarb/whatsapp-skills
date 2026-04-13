# WhatsApp Flow Skills

A collection of WhatsApp Flow generation skills and workspace data.

## Skills

### `whatsapp-flow-gen`
A specialized skill for building WhatsApp Flow packages consisting of the UI (`flow.json`) and the Backend logic (Flow Endpoint + Webhook).

#### Key Features
- **UI Generation**: Creates valid UI schemas for WhatsApp Flows.
- **Backend Logic**: Generates FastAPI-based backends for encrypted data exchange and standard webhook submissions.
- **`data_exchange_trigger` Pattern**: Implements a robust identifier for handling multiple intermediate transitions.

## Usage

To use this skill, mention it explicitly in your prompts to your AI assistant:

* "Use the `whatsapp-flow-gen` skill to create an appointment booking flow."
* "Create a WhatsApp Flow for collecting user feedback. Follow the rules in `whatsapp-flow-gen`."

## Installation

To install this skill in Gemini or other "vibe coding" AI tools that support the `.agents` specification:

1. **Direct Copy (Recommended):** Copy the entire `.agents` folder from this repository into the root directory of your project workspace. If you are using Gemini, it will automatically detect and load the skill.
2. **Manual Installation:** 
   * Create a folder named `.agents/skills/whatsapp-flow-gen/` in your workspace root.
   * Copy the `SKILL.md` (and any other related files like `RULES.md` depending on the skill schema) into this new directory.

## Workspace Data
The `whatsapp-flow-gen-workspace` directory contains the evaluation history and iterations used to refine the skill.

gemini skills install https://github.com/kritikumarb/whatsapp-skills.git --path .agents/skills/whatsapp-flow-gen
