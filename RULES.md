---
name: whatsapp-flows
description: >
  Expert knowledge base for building, validating, and debugging WhatsApp Flows
  using Flow JSON. Use this skill whenever the user wants to: create or edit a
  Flow JSON file, build a WhatsApp Flow screen or multi-screen experience, add
  interactive components (buttons, dropdowns, date pickers, checkboxes, media
  upload, carousels, etc.), configure routing between screens, wire up a Data
  Endpoint, handle dynamic/form data bindings, write conditional logic (If/Switch),
  implement media upload (PhotoPicker/DocumentPicker), decrypt CDN media, validate
  Flow JSON structure, or debug Flow JSON compilation errors. Trigger on any mention
  of "Flow JSON", "WhatsApp Flow", "flow screen", "wa flow", "flow component",
  "flow endpoint", or requests to build interactive WhatsApp experiences.
---

# WhatsApp Flows — Agent Skill

This skill contains the complete authoritative rules, constraints, and patterns
for authoring valid WhatsApp Flow JSON. Always consult this skill before writing
or modifying any Flow JSON. All rules below are mandatory unless explicitly marked
optional.

---

## 1. Top-Level Document Structure

Every Flow JSON document must follow this skeleton:

```json
{
  "version": "<string>",
  "screens": [ /* array of Screen objects */ ]
}
```

### 1.1 Required Top-Level Properties

| Property  | Type            | Rule                                                                 |
|-----------|-----------------|----------------------------------------------------------------------|
| `version` | string          | Must be a supported version string (e.g. `"3.1"`, `"6.0"`, `"7.1"`). Controls which features are available. |
| `screens` | array of Screen | At least one screen required. Cannot be empty.                      |

### 1.2 Optional Top-Level Properties

| Property            | Type   | Rule                                                                                                           |
|---------------------|--------|----------------------------------------------------------------------------------------------------------------|
| `routing_model`     | object | Required when a Data Endpoint is configured. Auto-generated if omitted and no endpoint is used.               |
| `data_api_version`  | string | Required when using a Data Endpoint. Currently must be `"3.0"`.                                              |
| `data_channel_uri`  | string | **Only for Flow JSON versions < 3.0.** For v3.0+, configure the endpoint URL via the Flows API `endpoint_uri` field instead. Do NOT include in v3.0+. |

### 1.3 Minimal Valid Example

```json
{
  "version": "6.0",
  "screens": [
    {
      "id": "WELCOME",
      "terminal": true,
      "layout": {
        "type": "SingleColumnLayout",
        "children": [
          { "type": "TextHeading", "text": "Hello!" },
          { "type": "Footer", "label": "Done", "on-click-action": { "name": "complete", "payload": {} } }
        ]
      }
    }
  ]
}
```

---

## 2. Routing Model Rules

Only declare `routing_model` when the Flow uses a Data Endpoint.

```json
"routing_model": {
  "SCREEN_A": ["SCREEN_B", "SCREEN_C"],
  "SCREEN_B": ["SCREEN_C"],
  "SCREEN_C": []
}
```

### 2.1 Mandatory Routing Rules

1. **Max 10 branches** — total number of edges across the whole graph cannot exceed 10.
2. **Exactly one entry screen** — a screen with no inbound edges is the entry point.
3. **No self-loops** — a screen cannot list itself as a route.
4. **Forward-only edges** — if A → B is declared, do NOT also declare B → A; back navigation is implicit.
5. **All paths terminate** — every possible path through the graph must end at a terminal screen.
6. **Terminal screens** — must have an empty array `[]` in the routing_model.
7. **Back navigation** — users can navigate Back between any two screens connected by an edge; this is automatic.

---

## 3. Screen Object Rules

```json
{
  "id": "UNIQUE_SCREEN_ID",
  "layout": { "type": "SingleColumnLayout", "children": [] }
}
```

### 3.1 Screen Properties

| Property         | Required | Type    | Rules                                                                                                                                         |
|------------------|----------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `id`             | ✅        | string  | Unique per Flow. `"SUCCESS"` is reserved — never use it. Use UPPER_SNAKE_CASE by convention.                                                 |
| `layout`         | ✅        | object  | Must have `type: "SingleColumnLayout"` and a `children` array. Max **50 components** per screen.                                             |
| `terminal`       | optional | boolean | Marks end state. Multiple terminal screens allowed. **A Footer component is mandatory on every terminal screen.**                             |
| `success`        | optional | boolean | Only on terminal screens. Defaults to `true`. Set `false` for cancellation/failure outcomes.                                                 |
| `title`          | optional | string  | Displayed in top navigation bar.                                                                                                              |
| `data`           | optional | object  | JSON Schema declaration for dynamic fields this screen expects. Every declared field **must** include `__example__`.                          |
| `refresh_on_back`| optional | boolean | Endpoint Flows only. Defaults to `false`. When `true`, triggers a Data Endpoint call when the user taps Back. Set on the screen being left, not the destination. |
| `sensitive`      | optional | array   | v5.1+. Array of field name strings whose values are masked in the Flow response summary.                                                     |

### 3.2 Data Declaration Pattern

```json
"data": {
  "field_name": {
    "type": "string",
    "__example__": "Example value"
  },
  "options_list": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id":    { "type": "string" },
        "title": { "type": "string" }
      }
    },
    "__example__": [{ "id": "1", "title": "Option A" }]
  }
}
```

**Rules:**
- `__example__` is **mandatory** on every declared data field.
- `null` type is **not supported**. Use `""` (empty string), omit the property, or send `undefined`.
- JSON Type Definition (RFC 8927) is used for type checking.

---

## 4. Dynamic Data Binding Syntax

| Syntax                                    | Meaning                                                       | Available Since |
|-------------------------------------------|---------------------------------------------------------------|-----------------|
| `"${data.field_name}"`                    | Data provided by server or `navigate` payload for this screen | All versions    |
| `"${form.field_name}"`                    | Value entered by the user in an input on this screen          | All versions    |
| `"${screen.SCREEN_ID.data.field_name}"`   | Read a data field from any named screen globally              | v4.0+           |
| `"${screen.SCREEN_ID.form.field_name}"`   | Read a form input from any named screen globally              | v4.0+           |

### 4.1 Nested Expression Syntax (v6.0+)

Wrap property value in backticks to enable expressions. The result type must match the property's expected type.

| Operation         | Operators          | Types Allowed                | Return Type |
|-------------------|--------------------|------------------------------|-------------|
| Equality          | `==`, `!=`         | string, number, boolean      | boolean     |
| Math comparison   | `<`, `<=`, `>`, `>=` | number                    | boolean     |
| Logical           | `&&`, `\|\|`       | boolean                      | boolean     |
| String concat     | space between parts | string, number, boolean     | string      |
| Arithmetic        | `+`, `-`, `/`, `%` | number                       | number      |

```json
"visible": "`${form.age} >= 18 && ${form.consent} == true`"
"text":    "`'Hello ' ${form.first_name} ', you are ' ${form.age} ' years old.'`"
```

**Rules:**
- Division or modulo by zero returns `0` (no NaN/error).
- To use a literal backtick inside, escape with `\\` before it: `\\\``.
- Cannot use expressions on `name` or `type` properties.

---

## 5. Actions

Actions are triggered by interactive components. Every action is declared under `on-click-action`, `on-select-action`, or `on-unselect-action`.

### 5.1 Action Reference

| Action          | Available Since | Payload        | Usage Rules                                                                                                               |
|-----------------|-----------------|----------------|---------------------------------------------------------------------------------------------------------------------------|
| `navigate`      | All             | Static JSON    | Pass data to next screen. **Never use on a terminal screen's Footer.** Data is accessible as `${data.*}` on target screen. |
| `complete`      | All             | Static JSON    | Terminates the Flow. Payload sent via webhook with `flow_token`. **Use only on terminal screens.**                        |
| `data_exchange` | All (endpoint) | Custom JSON    | Sends payload to Data Endpoint. Server returns next screen + data. Requires configured endpoint.                          |
| `update_data`   | v6.0+           | Static JSON    | Updates current screen state immediately. No navigation. Key must reference a declared `data` field on the current screen. |
| `open_url`      | v6.0+           | No payload     | Opens URL in device browser. Only `url` property accepted. **Only usable on `EmbeddedLink` and `OptIn` components.**     |

### 5.2 Action Structure

```json
// navigate
{
  "name": "navigate",
  "next": { "type": "screen", "name": "NEXT_SCREEN_ID" },
  "payload": { "key": "${form.field}" }
}

// complete
{
  "name": "complete",
  "payload": { "selected_plan": "${form.plan}" }
}

// data_exchange
{
  "name": "data_exchange",
  "payload": { "date": "${form.date}", "action_type": "fetch_slots" }
}

// update_data
{
  "name": "update_data",
  "payload": { "is_panel_visible": true }
}

// open_url
{
  "name": "open_url",
  "url": "https://example.com/terms"
}
```

### 5.3 Critical Action Rules

- **`complete` payload**: Include only user-entered data. Do NOT embed base64 images.
- **`navigate` restrictions**: PhotoPicker and DocumentPicker values are NOT allowed in `navigate` payloads. Use Global Dynamic References instead.
- **`open_url`**: No `payload` property accepted. Only `url`.

---

## 6. Forms

Forms collect user input. The `<Form>` wrapper component is **optional from v4.0+**.

### 6.1 Form Attributes

| Attribute       | Type            | Description                                                                                                  |
|-----------------|-----------------|--------------------------------------------------------------------------------------------------------------|
| `init-values`   | object          | Pre-populates fields. Key = component `name`. Value type must match component: Array\<string\> for CheckboxGroup, string for others. |
| `error-messages`| object          | Server-side validation errors. Key = component `name`, value = error string.                                |

### 6.2 Reference Form Data

```json
"payload": { "name": "${form.first_name}", "lang": "${form.language}" }
```

### 6.3 Component Availability Outside Form

| Component                                                           | Before v4.0 | v4.0+  |
|---------------------------------------------------------------------|-------------|--------|
| TextHeading, TextSubheading, TextBody, TextCaption, Footer, EmbeddedLink | ✅         | ✅     |
| TextInput, TextArea, CheckboxGroup, RadioButtonsGroup, OptIn, Dropdown, DatePicker | ❌ | ✅ |

---

## 7. Components — Complete Reference

**Global rules:**
- Max **50 components** per screen.
- Every component requires a `type` property.
- `name` property must be **unique per screen** for all input components.
- `visible` defaults to `true` for all components unless stated otherwise.

---

### 7.1 Text Components

#### TextHeading
```json
{ "type": "TextHeading", "text": "Title text", "visible": true }
```
- `text` required. Max **80 chars**. Cannot be blank/empty.

#### TextSubheading
```json
{ "type": "TextSubheading", "text": "Section heading" }
```
- `text` required. Max **80 chars**. Cannot be blank/empty.

#### TextBody
```json
{
  "type": "TextBody",
  "text": "Body text",
  "font-weight": "bold",
  "strikethrough": false,
  "markdown": true
}
```
- `text` required. Max **4096 chars**.
- `font-weight` enum: `bold | italic | bold_italic | normal`
- `markdown`: boolean. Default `false`. Requires v5.1+.
- Supported markdown (v5.1+): `**bold**`, `*italic*`, `~~strikethrough~~`, `[link](url)`, `+ unordered list`, `1. ordered list`

#### TextCaption
Same as TextBody but max **4096 chars**. Rendered smaller.

---

### 7.2 RichText (v5.1+)

```json
{
  "type": "RichText",
  "text": ["# Heading", "Paragraph 1", "Paragraph 2"]
}
```

- `text` is string or Array\<string\>. Dynamic binding supported.
- Supports full standard Markdown subset (see table below).
- **Until v6.2**: Must be **standalone** — no other components on the same screen.
- **From v6.3**: Can coexist with a `Footer` component.
- Images must be base64 inline only (`data:image/png;base64,...`). External URIs not supported.

**Markdown support matrix:**

| Syntax                       | RichText | TextBody | TextCaption |
|------------------------------|----------|----------|-------------|
| `# h1` / `## h2`             | ✅       | ❌       | ❌          |
| `**bold**` / `*italic*` / `~~strikethrough~~` | ✅ | ✅ | ✅ |
| `[link](url)`                | ✅       | ✅       | ✅          |
| `+ list` / `1. list`         | ✅       | ✅       | ✅          |
| `![img](data:image/...)`     | ✅       | ❌       | ❌          |
| Markdown table `\| col \|`   | ✅       | ❌       | ❌          |

---

### 7.3 TextInput

```json
{
  "type": "TextInput",
  "name": "email_field",
  "label": "Email address",
  "input-type": "email",
  "required": true,
  "min-chars": "5",
  "max-chars": "80",
  "helper-text": "Enter your work email",
  "pattern": "^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$"
}
```

| Property        | Required | Rules                                                                                          |
|-----------------|----------|------------------------------------------------------------------------------------------------|
| `name`          | ✅        | Unique on screen.                                                                              |
| `label`         | ✅        | Dynamic. Max **20 chars**.                                                                    |
| `input-type`    | optional | `text | number | email | password | passcode | phone`. Default: `text`.                      |
| `pattern`       | optional | Raw regex string (v6.2+). Requires `helper-text`. Supported with `text`, `number`, `password`, `passcode`. |
| `helper-text`   | optional | Dynamic. Max **80 chars**. Mandatory when `pattern` is set.                                   |
| `max-chars`     | optional | Dynamic. Default **80**.                                                                       |
| `label-variant` | optional | `"large"` — multi-line prominent label. v7.0+.                                               |
| `error-message` | optional | Dynamic. Max **30 chars**. Outside Form only (v4.0+).                                         |
| `init-value`    | optional | Dynamic. Outside Form only (v4.0+).                                                            |

---

### 7.4 TextArea

```json
{
  "type": "TextArea",
  "name": "message",
  "label": "Your message",
  "required": true,
  "max-length": "600"
}
```

| Property     | Required | Rules                                     |
|--------------|----------|-------------------------------------------|
| `name`       | ✅        | Unique on screen.                         |
| `label`      | ✅        | Dynamic. Max **20 chars**.                |
| `max-length` | optional | Dynamic. Default **600 chars**.           |
| `helper-text`| optional | Dynamic. Max **80 chars**.                |

---

### 7.5 CheckboxGroup

```json
{
  "type": "CheckboxGroup",
  "name": "days",
  "label": "Select days",
  "required": true,
  "min-selected-items": 1,
  "max-selected-items": 3,
  "data-source": [
    { "id": "mon", "title": "Monday" },
    { "id": "tue", "title": "Tuesday" }
  ]
}
```

| Limit             | Value                             |
|-------------------|-----------------------------------|
| Label             | Max 30 chars                      |
| Option title      | Max 30 chars                      |
| Option description| Max 300 chars                     |
| Option metadata   | Max 20 chars                      |
| Min options       | 1                                 |
| Max options       | 20                                |
| Image per option  | Max 300 KB (< v6.0) / 100 KB (v6.0+) |

- `data-source` items in v5.0+: add `image` (base64), `alt-text`, `color` (6-digit hex).
- `on-select-action`: `data_exchange` or `update_data` (v6.0+).
- `on-unselect-action`: `update_data` only (v6.0+).
- `init-value`: Array\<string\> — outside Form only (v4.0+).
- WEBP images not supported on iOS < 14.

---

### 7.6 RadioButtonsGroup

Same structure as CheckboxGroup but allows only **one selection**. `init-value` is a **single string** (not array).

---

### 7.7 Dropdown

```json
{
  "type": "Dropdown",
  "name": "plan",
  "label": "Select plan",
  "required": true,
  "data-source": [
    { "id": "basic", "title": "Basic" },
    { "id": "pro",   "title": "Pro" }
  ]
}
```

| Limit              | Value                              |
|--------------------|------------------------------------|
| Label              | Max 20 chars                       |
| Option title       | Max 30 chars                       |
| Max options        | 200 (no images) / 100 (with images)|
| Image per option   | Max 300 KB (< v6.0) / 100 KB (v6.0+) |

- Same `on-select-action` / `on-unselect-action` rules as CheckboxGroup.

---

### 7.8 Footer

```json
{
  "type": "Footer",
  "label": "Continue",
  "on-click-action": { "name": "navigate", "next": { "type": "screen", "name": "NEXT" }, "payload": {} },
  "left-caption": "Step 1",
  "right-caption": "of 3"
}
```

| Rule                                  | Detail                                                   |
|---------------------------------------|----------------------------------------------------------|
| Max per screen                        | **1 Footer** only                                        |
| Required on terminal screens          | Yes — mandatory                                          |
| `label` max chars                     | 35                                                       |
| `left-caption` / `right-caption`      | Max 15 chars each. Cannot combine with `center-caption`. |
| `center-caption`                      | Max 15 chars. Cannot combine with left+right captions.   |
| Footer inside `If` component          | Must exist in **both** `then` and `else` branches        |

---

### 7.9 OptIn

```json
{
  "type": "OptIn",
  "name": "terms_accepted",
  "label": "I agree to the Terms and Conditions",
  "required": true,
  "on-click-action": { "name": "open_url", "url": "https://example.com/terms" }
}
```

- Max **5 OptIn** components per screen.
- `label` max **120 chars**.
- `on-click-action` shows "Read more" link. Allowed: `data_exchange`, `navigate`, `open_url` (v6.0+).
- `on-select-action` / `on-unselect-action`: `update_data` only (v6.0+).

---

### 7.10 EmbeddedLink

```json
{
  "type": "EmbeddedLink",
  "text": "View full policy",
  "on-click-action": { "name": "open_url", "url": "https://example.com/policy" }
}
```

- Max **2 EmbeddedLink** components per screen.
- `text` max **25 chars**. Cannot be blank.
- `on-click-action` allowed: `data_exchange`, `navigate`, `open_url` (v6.0+).

---

### 7.11 DatePicker

```json
{
  "type": "DatePicker",
  "name": "appointment_date",
  "label": "Select date",
  "min-date": "2024-01-01",
  "max-date": "2024-12-31",
  "helper-text": "Choose a weekday"
}
```

| Property          | Version Rule                                              |
|-------------------|-----------------------------------------------------------|
| `min-date` / `max-date` | v4: timestamp in ms. **v5.0+: `"YYYY-MM-DD"` string (timezone-independent)** |
| `unavailable-dates` | v4: array of timestamps. v5.0+: array of `"YYYY-MM-DD"` strings |
| `on-select-action`  | `data_exchange` only                                    |

- **Warning**: Before v5.0, only works correctly when business and user are in the **same timezone**. Use v5.0+ for all new flows.
- `label` max **40 chars**. `helper-text` max **80 chars**. `error-message` max **80 chars**.

---

### 7.12 CalendarPicker (v6.1+)

```json
{
  "type": "CalendarPicker",
  "name": "vacation",
  "label": "Select dates",
  "mode": "range",
  "min-date": "2024-06-01",
  "max-date": "2024-08-31",
  "include-days": ["Mon","Tue","Wed","Thu","Fri"]
}
```

- `mode`: `"single"` (default) or `"range"`.
- In range mode, `label`, `helper-text`, `required`, `init-value`, `error-message` accept `{"start-date": ..., "end-date": ...}` objects.
- `min-days` / `max-days`: range mode only — min/max days between start and end.
- `on-select-action`: `data_exchange` only. Payload: `"YYYY-MM-DD"` (single) or `{"start-date":"YYYY-MM-DD","end-date":"YYYY-MM-DD"}` (range).
- All dates in `"YYYY-MM-DD"` format.

| Limit         | Value        |
|---------------|--------------|
| Title         | Max 80 chars |
| Description   | Max 300 chars|
| Label         | Max 40 chars |
| Helper text   | Max 80 chars |

---

### 7.13 Image

```json
{
  "type": "Image",
  "src": "${data.product_image}",
  "scale-type": "contain",
  "aspect-ratio": 1.5,
  "alt-text": "Product photo"
}
```

- `src`: base64-encoded image. Dynamic binding supported.
- `scale-type`: `contain` (default, preserves aspect ratio) | `cover` (clips to fill container).
- Max **3 Image** components per screen.
- Recommended size: ≤ **300 KB**. Supported formats: **JPEG, PNG**.
- **Android note**: for `contain`, set explicit `height` to avoid default 400px whitespace.

---

### 7.14 If (v4.0+)

```json
{
  "type": "If",
  "condition": "${form.age} >= 18",
  "then": [
    { "type": "TextBody", "text": "Adult content" }
  ],
  "else": [
    { "type": "TextBody", "text": "Under 18 content" }
  ]
}
```

**Condition rules:**
- Must contain at least one dynamic variable (`${data.*}` or `${form.*}`).
- Must resolve to `boolean`. Strings and numbers alone are not valid.
- Cannot be only static literals.

**Supported operators:** `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`, `()`

**Footer inside If rules:**
- Footer can only be in the **first (outermost)** `If`, not in nested `If` components.
- If Footer is in `then`, it must also be in `else` (and vice versa). `else` becomes mandatory.
- A Footer **outside** the `If` is not allowed if one exists inside.

**Nesting:** Max **3 levels** deep.

**Allowed child components:** TextHeading, TextSubheading, TextBody, TextCaption, CheckboxGroup, DatePicker, Dropdown, EmbeddedLink, Footer, Image, OptIn, RadioButtonsGroup, Switch, TextArea, TextInput, If, ChipsSelector (v7.1+).

---

### 7.15 Switch (v4.0+)

```json
{
  "type": "Switch",
  "value": "${data.plan_type}",
  "cases": {
    "basic": [{ "type": "TextBody", "text": "Basic plan selected" }],
    "pro":   [{ "type": "TextBody", "text": "Pro plan selected" }]
  }
}
```

- `cases` cannot be empty (`{}` is invalid — at least one key required).
- Same allowed child components as `If`.

---

### 7.16 NavigationList (v6.2+)

```json
{
  "type": "NavigationList",
  "name": "insurance_list",
  "list-items": "${data.insurances}",
  "on-click-action": { "name": "navigate", "next": { "type": "screen", "name": "DETAILS" }, "payload": {} }
}
```

| Constraint                                    | Value                                  |
|-----------------------------------------------|----------------------------------------|
| Max per screen                                | **2** (exclusive — no other components allowed on same screen) |
| Items per list                                | Min 1 / Max 20                         |
| Cannot use on terminal screen                 | Correct — not allowed                  |
| `on-click-action` definition                  | Either at component-level OR per-item, never both |
| `badge` items per list                        | Max **1**                              |
| `end` add-on + `media-size: large`            | Cannot combine                         |

**Item property limits:**

| Property                    | Limit           |
|-----------------------------|-----------------|
| `main-content.title`        | Max 30 chars    |
| `main-content.description`  | Max 20 chars    |
| `main-content.metadata`     | Max 80 chars    |
| `start.image`               | Max 100 KB      |
| `end.title/description/metadata` | Max 10 chars each |
| `badge`                     | Max 15 chars    |
| `tags` items / per tag      | Max 3 / 15 chars|

---

### 7.17 ChipsSelector (v6.3+)

```json
{
  "type": "ChipsSelector",
  "name": "interests",
  "label": "Choose your interests",
  "data-source": [
    { "id": "tech", "title": "Technology", "enabled": true },
    { "id": "sport", "title": "Sports", "enabled": true }
  ],
  "min-selected-items": 1,
  "max-selected-items": 5
}
```

- Min **2** / Max **20** options in `data-source`.
- `label` max **80 chars**. `description` max **300 chars**.
- `on-select-action`: `data_exchange` or `update_data` (update_data: v7.1+).
- `on-unselect-action`: `update_data` only (v7.1+).

---

### 7.18 ImageCarousel (v7.1+)

```json
{
  "type": "ImageCarousel",
  "images": "${data.product_images}",
  "aspect-ratio": "16:9",
  "scale-type": "cover"
}
```

| Limit                       | Value             |
|-----------------------------|-------------------|
| Images per carousel         | Min 1 / Max 3     |
| Carousels per screen        | Max 2             |
| Carousels per Flow          | Max 3             |
| `aspect-ratio`              | `"4:3"` (default) or `"16:9"` |
| `scale-type`                | `"contain"` (default) or `"cover"` |

Each image item: `{ "src": "<base64>", "alt-text": "<string>" }` — both required.

---

## 8. Media Upload Components

> ⚠️ **Not supported by the On-Premise API.** Must use Cloud API.
> ⚠️ WhatsApp does not guarantee uploaded media is non-malicious. Always validate server-side.

**Mutual exclusion rule:** Only **one** of PhotoPicker or DocumentPicker per screen. They **cannot coexist**.

---

### 8.1 PhotoPicker (v4.0+)

```json
{
  "type": "PhotoPicker",
  "name": "selfie",
  "label": "Upload your photo",
  "description": "Take a photo or choose from gallery",
  "photo-source": "camera_gallery",
  "min-uploaded-photos": 1,
  "max-uploaded-photos": 1,
  "max-file-size-kb": 5120
}
```

| Property              | Default       | Range     |
|-----------------------|---------------|-----------|
| `photo-source`        | `camera_gallery` | `camera_gallery | camera | gallery` |
| `max-file-size-kb`    | 25600 (25 MiB)| 1–25600   |
| `min-uploaded-photos` | 0 (optional)  | 0–30      |
| `max-uploaded-photos` | 30            | 1–30      |

**Restrictions:**
- Max **1** PhotoPicker per screen.
- **Cannot** use `init-values` on Form to pre-populate PhotoPicker.
- **Not allowed** in `navigate` action payload.
- In `data_exchange` or `complete` payload: must be a **top-level value only** — not nested inside an object:
  ```json
  // ✅ Correct
  "payload": { "media": "${form.selfie}" }
  // ❌ Wrong — nested
  "payload": { "media": { "photo": "${form.selfie}" } }
  ```
- Response message: max **10 files**, max **100 MiB** aggregate.

---

### 8.2 DocumentPicker (v4.0+)

```json
{
  "type": "DocumentPicker",
  "name": "kyc_doc",
  "label": "Upload ID document",
  "allowed-mime-types": ["application/pdf", "image/jpeg", "image/png"],
  "min-uploaded-documents": 1,
  "max-uploaded-documents": 2
}
```

Same restrictions as PhotoPicker. Same payload nesting rule applies.

**Supported MIME types** (default: all):
`application/pdf`, `application/msword`, `.wordprocessingml.document`, `application/vnd.ms-excel`, `.spreadsheetml.sheet`, `application/vnd.ms-powerpoint`, `.presentationml.presentation`, `application/vnd.oasis.opendocument.*`, `application/gzip`, `application/zip`, `application/x-7z-compressed`, `image/avif`, `image/gif`, `image/heic`, `image/heif`, `image/jpeg`, `image/png`, `image/tiff`, `image/webp`, `text/plain`, `video/mp4`, `video/mpeg`

> Note: `image/jpeg` in `allowed-mime-types` also enables gallery photo selection.

---

### 8.3 Media Handling on Your Server (Endpoint)

Uploaded files are stored encrypted on WhatsApp CDN for up to **20 days**.

**Endpoint payload structure:**
```json
"photo_picker": [{
  "media_id": "790aba14-5f4a-4dbd-aa9e-0d75401da14b",
  "cdn_url": "https://mmg.whatsapp.net/v/...",
  "file_name": "photo.jpg",
  "encryption_metadata": {
    "encrypted_hash": "...",
    "iv": "...",
    "encryption_key": "...",
    "hmac_key": "...",
    "plaintext_hash": "..."
  }
}]
```

**Decryption algorithm:** AES256-CBC + HMAC-SHA256 + PKCS7. CDN file = `ciphertext ‖ hmac10`.

**Decryption steps (mandatory order):**
1. Download file from `cdn_url`.
2. Verify: `SHA256(cdn_file) == encrypted_hash`.
3. Validate HMAC: compute `HMAC-SHA256(hmac_key, iv, ciphertext)` — first 10 bytes must match `hmac10`.
4. Decrypt: AES-CBC with `iv` on ciphertext → remove PKCS7 padding → `decrypted_media`.
5. Verify plaintext: `SHA256(decrypted_media) == plaintext_hash`.

---

## 9. Global Limits & Constraints

| Constraint                        | Limit                           |
|-----------------------------------|---------------------------------|
| Flow JSON file size               | Max **10 MB**                   |
| Components per screen             | Max **50**                      |
| Routing model branches            | Max **10** edges                |
| Image components per screen       | Max **3**                       |
| OptIn per screen                  | Max **5**                       |
| EmbeddedLink per screen           | Max **2**                       |
| NavigationList per screen         | Max **2** (exclusive)           |
| ImageCarousel per screen / per Flow | Max 2 / 3                    |
| PhotoPicker or DocumentPicker     | Max **1** per screen (mutually exclusive) |
| Response message media files      | Max **10** files, **100 MiB** aggregate |
| Max upload file size              | **25 MiB** per file             |
| CDN media retention               | Up to **20 days**               |
| If nesting depth                  | Max **3 levels**                |
| Dropdown options (no images)      | Max **200**                     |
| Dropdown options (with images)    | Max **100**                     |
| CheckboxGroup / RadioButtonsGroup options | Max **20**             |
| ChipsSelector options             | Min **2** / Max **20**          |
| NavigationList items              | Min **1** / Max **20**          |
| Data channel payload size         | Max **1 MB**                    |

---

## 10. Version Feature Matrix

| Version | Key Features Added                                                                 |
|---------|------------------------------------------------------------------------------------|
| < 3.0   | `data_channel_uri` in Flow JSON (deprecated in v3.0+)                             |
| v3.0    | `data_channel_uri` moved to Flows API `endpoint_uri`                              |
| v4.0    | Optional Form wrapper; PhotoPicker; DocumentPicker; If; Switch; Global references |
| v5.0    | DatePicker YYYY-MM-DD format (timezone-independent); image/color in data-source   |
| v5.1    | RichText component; markdown in TextBody/TextCaption; `sensitive` field masking   |
| v6.0    | `update_data` action; `open_url` action; `on-unselect-action`; nested expressions |
| v6.1    | CalendarPicker                                                                     |
| v6.2    | NavigationList; TextInput `pattern` regex validation                               |
| v6.3    | ChipsSelector; RichText + Footer coexistence                                       |
| v7.0    | `label-variant: "large"` for TextInput / TextArea                                 |
| v7.1    | ImageCarousel; ChipsSelector `update_data` on-select/unselect; ChipsSelector in If/Switch |

---

## 11. Common Mistakes & How to Avoid Them

| Mistake                                          | Rule / Fix                                                                                 |
|--------------------------------------------------|--------------------------------------------------------------------------------------------|
| Using `"SUCCESS"` as screen id                   | Reserved keyword — use any other unique id                                                 |
| No Footer on terminal screen                     | Every terminal screen requires exactly one Footer                                           |
| `navigate` action on terminal screen Footer      | Use `complete` instead                                                                     |
| `data_channel_uri` in v3.0+ Flow JSON            | Remove it; configure the endpoint via Flows API `endpoint_uri`                             |
| Missing `__example__` on declared data field      | Every field in `data` block must include `__example__`                                     |
| Using `null` as a data value                     | Use `""`, `undefined`, or omit the property                                                |
| PhotoPicker / DocumentPicker in navigate payload | Not allowed. Use `${screen.SCREEN_ID.form.field}` global reference instead                 |
| Nesting media picker value in payload object     | Must be top-level: `"payload": { "media": "${form.photo}" }` not nested                   |
| PhotoPicker + DocumentPicker on same screen      | Mutually exclusive — only one allowed per screen                                            |
| RichText with other components (< v6.3)          | RichText must be standalone until v6.3 (Footer coexistence allowed from v6.3)              |
| Footer in nested `If` (level 2+)                 | Footer only allowed in the outermost `If`                                                  |
| Footer in `then` but not in `else`               | Must appear in both branches or neither                                                     |
| Empty `cases` in Switch                          | At least one key-value pair required                                                       |
| NavigationList on terminal screen                | Not allowed                                                                                |
| NavigationList mixed with other components       | Exclusive — NavigationList screens cannot have any other component types                   |
| `on-click-action` on NavigationList at both component and item level | Must be one or the other, not both               |
| Using DatePicker timestamps (ms) in v5.0+        | Use `"YYYY-MM-DD"` strings instead                                                        |
| Backtick expression returning non-boolean for `visible` | Expression must resolve to boolean type                                           |
| `open_url` on components other than EmbeddedLink/OptIn | Only these two components support `open_url`                                    |
| Routing model with back-edge declared            | Only forward edges. If A→B declared, don't also declare B→A.                               |
| More than 10 routing model edges                 | Reduce branching — max 10 total connections                                                |
| More than 50 components on a screen              | Split into multiple screens                                                                |

---

## 12. Sensitive Field Masking Reference

When fields are listed in a screen's `sensitive` array, the response summary shown to users masks them as follows:

| Component                                     | Masking Applied         |
|-----------------------------------------------|-------------------------|
| TextInput / TextArea / DatePicker / Dropdown  | Masked (`••••••••••••`) |
| CheckboxGroup / RadioButtonsGroup             | Masked (`••••••••••••`) |
| Password / OTP                                | Hidden completely       |
| OptIn                                         | Shown as-is (no masking)|
| DocumentPicker / PhotoPicker                  | File hidden completely  |

---

## 13. Agent Workflow — Building a Flow

When asked to create or modify a Flow, follow this sequence:

1. **Identify the version** — ask or infer from context. Default to latest stable (`"7.1"`) unless constraints exist.
2. **Map the screens** — list all screens, which are terminal, and what data flows between them.
3. **Define routing_model** — only if endpoint is used. Check: one entry, all paths end at terminal, ≤ 10 edges.
4. **Declare screen `data` blocks** — for each screen needing server/dynamic data; always include `__example__`.
5. **Place components** — respect all per-screen limits. Check component version availability.
6. **Wire actions** — `navigate` for forward transitions, `complete` on terminal Footer, `data_exchange` for server calls.
7. **Add dynamic bindings** — use `${data.*}`, `${form.*}`, or global `${screen.*.*.*}` as needed.
8. **Validate**:
   - No `"SUCCESS"` screen id
   - Every terminal screen has Footer
   - No `navigate` on terminal Footer
   - `__example__` on all data fields
   - Component count ≤ 50 per screen
   - Routing rules satisfied
   - Version-gated features match declared version

---

*Source: Meta for Developers — WhatsApp Flows Reference*
*Pages: /reference/flowjson | /reference/components | /reference/media_upload*