# WhatsApp Flows — Authoritative Rules

This reference contains the complete authoritative rules, constraints, and patterns for authoring valid WhatsApp Flow JSON.

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

---

## 5. Actions

### 5.1 Action Reference

| Action          | Available Since | Payload        | Usage Rules                                                                                                               |
|-----------------|-----------------|----------------|---------------------------------------------------------------------------------------------------------------------------|
| `navigate`      | All             | Static JSON    | Pass data to next screen. **Never use on a terminal screen's Footer.** Data is accessible as `${data.*}` on target screen. |
| `complete`      | All             | Static JSON    | Terminates the Flow. Payload sent via webhook with `flow_token`. **Use only on terminal screens.**                        |
| `data_exchange` | All (endpoint) | Custom JSON    | Sends payload to Data Endpoint. Server returns next screen + data. Requires configured endpoint.                          |
| `update_data`   | v6.0+           | Static JSON    | Updates current screen state immediately. No navigation. Key must reference a declared `data` field on the current screen. |
| `open_url`      | v6.0+           | No payload     | Opens URL in device browser. Only `url` property accepted. **Only usable on `EmbeddedLink` and `OptIn` components.**     |

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

---

## 7. Components — Complete Reference

**Global rules:**
- Max **50 components** per screen.
- Every component requires a `type` property.
- `name` property must be **unique per screen** for all input components.

---

### 7.1 Text Components

#### TextHeading
- `text` required. Max **80 chars**.

#### TextSubheading
- `text` required. Max **80 chars**.

#### TextBody
- `text` required. Max **4096 chars**.
- `font-weight` enum: `bold | italic | bold_italic | normal`
- `markdown`: boolean. Default `false`. Requires v5.1+.

#### TextCaption
Same as TextBody but rendered smaller. Max **4096 chars**.

---

### 7.2 RichText (v5.1+)

- `text` is string or Array\<string\>.
- **Until v6.2**: Must be **standalone** — no other components on the same screen.
- **From v6.3**: Can coexist with a `Footer` component.

---

### 7.3 TextInput

| Property        | Rules                                                                                          |
|-----------------|------------------------------------------------------------------------------------------------|
| `label`         | Max **20 chars**.                                                                             |
| `input-type`    | `text | number | email | password | passcode | phone`.                                           |
| `max-chars`     | Default **80**.                                                                                |
| `helper-text`   | Max **80 chars**. Mandatory when `pattern` is set.                                            |

---

### 7.4 TextArea

- `label` max **20 chars**.
- `max-length` default **600 chars**.

---

### 7.5 CheckboxGroup / 7.6 RadioButtonsGroup

- `data-source` max **20 options**.
- Label max **30 chars**, Option title max **30 chars**.

---

### 7.7 Dropdown

- Max **200 options** (no images) / **100 options** (with images).
- Label max **20 chars**, Option title max **30 chars**.

---

### 7.8 Footer

- **1 Footer** only per screen.
- Mandatory on terminal screens.
- `label` max **35 chars**.

---

### 7.9 OptIn

- Max **5** per screen.
- `label` max **120 chars**.

---

### 7.10 EmbeddedLink

- Max **2** per screen.
- `text` max **25 chars**.

---

### 7.11 DatePicker

- **v5.0+: `"YYYY-MM-DD"` string** (timezone-independent).
- `label` max **40 chars**.

---

### 7.12 CalendarPicker (v6.1+)

- `mode`: `"single"` or `"range"`.
- All dates in `"YYYY-MM-DD"` format.

---

### 7.13 Image

- `src`: base64-encoded image.
- Max **3** per screen.

---

### 7.14 If / 7.15 Switch (v4.0+)

- Footer can only be in the **first (outermost)** `If`.
- If Footer is in `then`, it must also be in `else`.
- `If` nesting: Max **3 levels** deep.

---

### 7.16 NavigationList (v6.2+)

- Max **2** per screen (exclusive).
- Items: Min 1 / Max 20.
- Cannot use on terminal screen.

---

### 7.17 ChipsSelector (v6.3+)

- Min **2** / Max **20** options.
- `label` max **80 chars**.

---

### 7.18 ImageCarousel (v7.1+)

- Images: Min 1 / Max 3.
- Max 2 per screen / 3 per Flow.

---

## 8. Media Upload Components (PhotoPicker / DocumentPicker)

- Only **one** per screen (mutually exclusive).
- **Not allowed** in `navigate` action payload.
- Payload nesting rule: must be a **top-level value only**.
- Max **10 files**, **100 MiB** aggregate per message.

---

## 9. Global Limits & Constraints

| Constraint                        | Limit                           |
|-----------------------------------|---------------------------------|
| Flow JSON file size               | Max **10 MB**                   |
| Components per screen             | Max **50**                      |
| Routing model branches            | Max **10** edges                |
| If nesting depth                  | Max **3 levels**                |

---

## 11. Common Mistakes & How to Avoid Them

- Using `"SUCCESS"` as screen id.
- No Footer on terminal screen.
- `navigate` action on terminal screen Footer.
- Missing `__example__` on declared data field.
- PhotoPicker / DocumentPicker in navigate payload.
- Nesting media picker value in payload object.

---

## 13. Agent Workflow — Building a Flow

1. **Identify version** (default `"7.1"`).
2. **Map screens** (identify terminal, data flow).
3. **Define routing_model** (if endpoint used).
4. **Declare screen `data` blocks** (include `__example__`).
5. **Place components** (check limits and version).
6. **Wire actions** (`navigate`, `complete`, `data_exchange`).
7. **Add dynamic bindings**.
8. **Validate**.
