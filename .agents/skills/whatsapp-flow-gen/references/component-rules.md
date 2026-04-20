# WhatsApp Flows — Component Ruleset

> **Purpose:** This file is a machine-readable ruleset for the `whatsapp-flows` skill agent.
> Every rule is **mandatory** unless tagged `[OPTIONAL]`. Rules are grouped by component.
> The agent MUST check applicable rules before emitting any component JSON.

---

## HOW TO USE THIS RULESET

1. Identify which component(s) are being authored or validated.
2. Locate the component section below.
3. Apply **all** rules in that section — Universal Rules first, then component-specific rules.
4. If a rule is violated, **refuse to emit the invalid JSON** and explain the violation.
5. Cross-check with the **Cross-Component Exclusivity Rules** (Section 2) for screen-level conflicts.

---

## SECTION 1 — UNIVERSAL RULES (apply to every component)

These rules apply to **all** components without exception.

| Rule ID | Rule |
|---------|------|
| `U-001` | Every component MUST have a `type` property. |
| `U-002` | The `type` value MUST exactly match the documented string (case-sensitive). |
| `U-003` | Every input component MUST have a `name` property that is **unique within its screen**. |
| `U-004` | `name` and `type` properties MUST NOT use dynamic binding expressions (`${...}`). |
| `U-005` | `visible` defaults to `true` on all components; setting it explicitly is `[OPTIONAL]`. |
| `U-006` | Dynamic binding syntax is `"${data.field}"` or `"${form.field}"` or `"${screen.ID.(data\|form).field}"`. No other format is valid. |
| `U-007` | A screen MUST NOT exceed **50 components** total (including nested components inside `If`/`Switch`). |
| `U-008` | `null` is NOT a valid value for any property. Use `""`, omit the field, or send `undefined`. |
| `U-009` | Version-gated properties MUST NOT be used unless the Flow's declared `version` meets or exceeds the stated minimum. |
| `U-010` | Empty string `""` and blank/whitespace-only strings are NOT accepted for `text`, `label`, or `name` properties. |

---

## SECTION 2 — CROSS-COMPONENT EXCLUSIVITY RULES

Rules that govern which components can or cannot coexist on the same screen.

| Rule ID | Rule |
|---------|------|
| `X-001` | A screen MUST contain exactly **one** `Footer` component. |
| `X-002` | `Footer` is **mandatory** on every terminal screen (`terminal: true`). |
| `X-003` | `PhotoPicker` and `DocumentPicker` are **mutually exclusive** — only one may appear per screen. |
| `X-004` | `NavigationList` is **exclusive** — if a screen contains a `NavigationList`, it MUST NOT contain any other component type (including text components). |
| `X-005` | `RichText` is **standalone-only** until v6.2. From v6.3, a `Footer` may coexist with `RichText` on the same screen. No other components are allowed alongside `RichText`. |
| `X-006` | `Footer` inside an `If` component MUST exist in **both** `then` and `else` branches. |
| `X-007` | When a `Footer` exists inside an `If`, NO `Footer` may exist outside the `If` on the same screen. |
| `X-008` | `Footer` may only appear inside the **outermost** (level 1) `If` — NOT inside nested `If` components. |
| `X-009` | A screen MUST NOT contain more than **3** `Image` components. |
| `X-010` | A screen MUST NOT contain more than **5** `OptIn` components. |
| `X-011` | A screen MUST NOT contain more than **2** `EmbeddedLink` components. |
| `X-012` | A screen MUST NOT contain more than **2** `NavigationList` components. |
| `X-013` | A screen MUST NOT contain more than **2** `ImageCarousel` components. |
| `X-014` | A single Flow MUST NOT contain more than **3** `ImageCarousel` components total. |
| `X-015` | `NavigationList` MUST NOT appear on a terminal screen. |

---

## SECTION 3 — TEXT COMPONENTS

### 3.1 TextHeading

**Type string:** `"TextHeading"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TH-001` | `text` | **Required.** Max **80 characters**. Cannot be blank or whitespace-only. |
| `TH-002` | `text` | Supports dynamic binding: `"${data.field}"`. |
| `TH-003` | `visible` | `[OPTIONAL]` Boolean or dynamic boolean string. Default: `true`. |

---

### 3.2 TextSubheading

**Type string:** `"TextSubheading"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TS-001` | `text` | **Required.** Max **80 characters**. Cannot be blank or whitespace-only. |
| `TS-002` | `text` | Supports dynamic binding: `"${data.field}"`. |
| `TS-003` | `visible` | `[OPTIONAL]` Boolean or dynamic boolean string. Default: `true`. |

---

### 3.3 TextBody

**Type string:** `"TextBody"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TB-001` | `text` | **Required.** Max **4096 characters**. Cannot be blank or whitespace-only. |
| `TB-002` | `text` | Supports dynamic binding. |
| `TB-003` | `font-weight` | `[OPTIONAL]` Enum: `bold \| italic \| bold_italic \| normal`. Supports dynamic binding. |
| `TB-004` | `strikethrough` | `[OPTIONAL]` Boolean. Supports dynamic binding. |
| `TB-005` | `markdown` | `[OPTIONAL]` Boolean. Default: `false`. Requires Flow JSON **v5.1+**. |
| `TB-006` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `TB-007` | Markdown | When `markdown: true`, supported syntax: `**bold**`, `*italic*`, `~~strikethrough~~`, `[text](url)`, `+ list item`, `1. list item`. No heading syntax (`#`) supported. |

---

### 3.4 TextCaption

**Type string:** `"TextCaption"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TC-001` | `text` | **Required.** Max **4096 characters**. Cannot be blank or whitespace-only. |
| `TC-002` | `text` | Supports dynamic binding. |
| `TC-003` | `font-weight` | `[OPTIONAL]` Enum: `bold \| italic \| bold_italic \| normal`. Supports dynamic binding. |
| `TC-004` | `strikethrough` | `[OPTIONAL]` Boolean. Supports dynamic binding. |
| `TC-005` | `markdown` | `[OPTIONAL]` Boolean. Default: `false`. Requires Flow JSON **v5.1+**. |
| `TC-006` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

### 3.5 RichText

**Type string:** `"RichText"` — **Minimum version: v5.1**

| Rule ID | Property | Rule |
|---------|----------|------|
| `RT-001` | `text` | **Required.** String or Array\<string\>. Supports dynamic binding. |
| `RT-002` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `RT-003` | Screen exclusivity | Until v6.2: RichText MUST be the **only** component on the screen (cross-ref `X-005`). |
| `RT-004` | Screen exclusivity | From v6.3: RichText MAY coexist with a single `Footer`. No other components allowed. |
| `RT-005` | Images | Images inside RichText MUST be **base64 inline** only (`data:image/png;base64,...`). External URIs are NOT supported. |
| `RT-006` | Heading syntax | Only `# h1` and `## h2` render as heading components. `### h3` through `###### h6` render as `TextBody`. |
| `RT-007` | Markdown support | Supported: `**bold**`, `*italic*`, `~~strikethrough~~`, `[link](url)`, `![img](base64)`, `+ list`, `1. list`, markdown tables. |
| `RT-008` | Tables | Column width is determined by header content length. No custom column-width syntax available. |
| `RT-009` | Paragraphs | Created by separating items with a blank array element or blank line in the markdown string. |

---

## SECTION 4 — INPUT COMPONENTS

### 4.1 TextInput

**Type string:** `"TextInput"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TI-001` | `name` | **Required.** Unique string on the screen. |
| `TI-002` | `label` | **Required.** Dynamic. Max **20 characters**. |
| `TI-003` | `label-variant` | `[OPTIONAL]` Value: `"large"`. Multi-line prominent label. **Requires v7.0+**. |
| `TI-004` | `input-type` | `[OPTIONAL]` Enum: `text \| number \| email \| password \| passcode \| phone`. Default: `text`. |
| `TI-005` | `pattern` | `[OPTIONAL]` Raw regex string (no surrounding `/`). **Requires v6.2+**. Supported with `text`, `number`, `password`, `passcode` input types only. |
| `TI-006` | `pattern` dependency | When `pattern` is set, `helper-text` is **mandatory**. |
| `TI-007` | `required` | `[OPTIONAL]` Boolean. Supports dynamic binding. |
| `TI-008` | `min-chars` | `[OPTIONAL]` String or number. Supports dynamic binding. |
| `TI-009` | `max-chars` | `[OPTIONAL]` String or number. Default: **80**. Supports dynamic binding. |
| `TI-010` | `helper-text` | `[OPTIONAL]` Dynamic. Max **80 characters**. |
| `TI-011` | `init-value` | `[OPTIONAL]` Dynamic. Available **outside Form only**. **Requires v4.0+**. |
| `TI-012` | `error-message` | `[OPTIONAL]` Dynamic. Max **30 characters**. Outside Form only. **Requires v4.0+**. |
| `TI-013` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

### 4.2 TextArea

**Type string:** `"TextArea"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `TA-001` | `name` | **Required.** Unique string on the screen. |
| `TA-002` | `label` | **Required.** Dynamic. Max **20 characters**. |
| `TA-003` | `label-variant` | `[OPTIONAL]` Value: `"large"`. **Requires v7.0+**. |
| `TA-004` | `required` | `[OPTIONAL]` Boolean. Supports dynamic binding. |
| `TA-005` | `max-length` | `[OPTIONAL]` Dynamic. Default: **600 characters**. |
| `TA-006` | `helper-text` | `[OPTIONAL]` Dynamic. Max **80 characters**. |
| `TA-007` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `TA-008` | `init-value` | `[OPTIONAL]` Dynamic. Outside Form only. **Requires v4.0+**. |
| `TA-009` | `error-message` | `[OPTIONAL]` Dynamic. Outside Form only. **Requires v4.0+**. |
| `TA-010` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

### 4.3 CheckboxGroup

**Type string:** `"CheckboxGroup"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `CG-001` | `name` | **Required.** Unique string on the screen. |
| `CG-002` | `label` | Required from **v4.0+**; optional before v4.0. Dynamic. Max **30 characters**. |
| `CG-003` | `data-source` | **Required.** Array of option objects or dynamic binding. Min **1** item. Max **20** items. |
| `CG-004` | `data-source` item shape (all versions) | Each item: `{ "id": string, "title": string }`. Also accepts: `description` (max 300 chars), `metadata` (max 20 chars), `enabled` (boolean). |
| `CG-005` | `data-source` item shape (v5.0+) | Adds: `image` (base64 string, max 300 KB before v6.0 / max **100 KB** from v6.0), `alt-text` (string), `color` (6-digit hex string). |
| `CG-006` | `data-source` item shape (v6.0+) | Adds: `on-select-action` (`update_data` action object), `on-unselect-action` (`update_data` action object). |
| `CG-007` | `min-selected-items` | `[OPTIONAL]` Integer. Dynamic binding supported. |
| `CG-008` | `max-selected-items` | `[OPTIONAL]` Integer. Dynamic binding supported. Must be ≥ `min-selected-items`. |
| `CG-009` | `required` | `[OPTIONAL]` Boolean. Dynamic binding supported. |
| `CG-010` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `CG-011` | `description` | `[OPTIONAL]` Dynamic. **Requires v4.0+**. |
| `CG-012` | `media-size` | `[OPTIONAL]` Enum: `regular \| large`. **Requires v5.0+**. Supports dynamic binding. |
| `CG-013` | `on-select-action` | `[OPTIONAL]` Allowed values: `data_exchange` (all versions) or `update_data` (**v6.0+** only). |
| `CG-014` | `on-unselect-action` | `[OPTIONAL]` **Requires v6.0+**. Only `update_data` allowed. When defined, handles unselect exclusively; `on-select-action` then handles select only. When omitted, `on-select-action` handles both events. |
| `CG-015` | `init-value` | `[OPTIONAL]` Array\<string\>. Outside Form only. **Requires v4.0+**. |
| `CG-016` | `error-message` | `[OPTIONAL]` Dynamic string. Outside Form only. **Requires v4.0+**. |
| `CG-017` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `CG-018` | WEBP images | WEBP format images in `data-source` are NOT supported on iOS versions prior to iOS 14. |

---

### 4.4 RadioButtonsGroup

**Type string:** `"RadioButtonsGroup"`

All rules from `CG-001` through `CG-018` apply, with these differences:

| Rule ID | Property | Rule |
|---------|----------|------|
| `RB-001` | Single selection | RadioButtonsGroup allows only **one** selected item. No `min-selected-items` / `max-selected-items` properties. |
| `RB-002` | `init-value` | **Single string** — NOT an array. Outside Form only. **Requires v4.0+**. |

---

### 4.5 Dropdown

**Type string:** `"Dropdown"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `DD-001` | `name` | **Required.** Unique string on the screen. |
| `DD-002` | `label` | **Required.** Max **20 characters**. |
| `DD-003` | `data-source` | **Required.** Array of option objects or dynamic binding. Min **1** item. |
| `DD-004` | `data-source` max items | Max **200** items when no images present. Max **100** items when images are present in `data-source`. |
| `DD-005` | `data-source` item shape | Same evolution as CheckboxGroup: base shape → v5.0 adds image/color → v6.0 adds on-select/unselect-action. |
| `DD-006` | Image max size | Max **300 KB** per image before v6.0. Max **100 KB** from v6.0+. |
| `DD-007` | `required` | `[OPTIONAL]` Boolean. Dynamic binding supported. |
| `DD-008` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `DD-009` | `on-select-action` | `[OPTIONAL]` Allowed: `data_exchange` or `update_data` (**v6.0+** for `update_data`). |
| `DD-010` | `on-unselect-action` | `[OPTIONAL]` **Requires v6.0+**. Only `update_data` allowed. Same event-splitting behaviour as CheckboxGroup. |
| `DD-011` | `init-value` | `[OPTIONAL]` String. Outside Form only. |
| `DD-012` | `error-message` | `[OPTIONAL]` Dynamic string. Outside Form only. |
| `DD-013` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `DD-014` | WEBP images | Not supported on iOS < 14. |

---

### 4.6 OptIn

**Type string:** `"OptIn"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `OI-001` | `name` | **Required.** Unique string on the screen. |
| `OI-002` | `label` | **Required.** Dynamic. Max **120 characters**. |
| `OI-003` | `required` | `[OPTIONAL]` Boolean. Dynamic binding supported. |
| `OI-004` | `on-click-action` | `[OPTIONAL]` Reveals a "Read more" link. Allowed actions: `data_exchange`, `navigate`. `open_url` also allowed from **v6.0+**. |
| `OI-005` | `on-select-action` | `[OPTIONAL]` **Requires v6.0+**. Only `update_data` allowed. |
| `OI-006` | `on-unselect-action` | `[OPTIONAL]` **Requires v6.0+**. Only `update_data` allowed. |
| `OI-007` | `init-value` | `[OPTIONAL]` Boolean. Outside Form only. **Requires v4.0+**. |
| `OI-008` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `OI-009` | Screen limit | Max **5** OptIn components per screen (cross-ref `X-010`). |

---

### 4.7 DatePicker

**Type string:** `"DatePicker"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `DP-001` | `name` | **Required.** Unique string on the screen. |
| `DP-002` | `label` | **Required.** Dynamic. Max **40 characters**. |
| `DP-003` | `min-date` | `[OPTIONAL]` Before v5.0: timestamp in milliseconds. **v5.0+: `"YYYY-MM-DD"` string (MANDATORY format for v5.0+)**. |
| `DP-004` | `max-date` | `[OPTIONAL]` Same format rules as `min-date`. |
| `DP-005` | `unavailable-dates` | `[OPTIONAL]` Before v5.0: Array of timestamps. **v5.0+: Array of `"YYYY-MM-DD"` strings**. |
| `DP-006` | Date format (v5.0+) | ALL date values (min, max, unavailable, init-value, returned payload) MUST use `"YYYY-MM-DD"` format. Timestamps in ms are deprecated. |
| `DP-007` | Timezone warning | Before v5.0: only works correctly when business and user are in the **same timezone**. Strongly recommend using v5.0+. |
| `DP-008` | `helper-text` | `[OPTIONAL]` Dynamic. Max **80 characters**. |
| `DP-009` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `DP-010` | `on-select-action` | `[OPTIONAL]` **Only `data_exchange` is supported.** `navigate` and `update_data` are NOT valid here. |
| `DP-011` | `init-value` | `[OPTIONAL]` Dynamic. Outside Form only. **Requires v4.0+**. |
| `DP-012` | `error-message` | `[OPTIONAL]` Dynamic. Max **80 characters**. Outside Form only. **Requires v4.0+**. |
| `DP-013` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

### 4.8 CalendarPicker

**Type string:** `"CalendarPicker"` — **Minimum version: v6.1**

| Rule ID | Property | Rule |
|---------|----------|------|
| `CP-001` | `name` | **Required.** Unique string on the screen. |
| `CP-002` | `label` | **Required.** Dynamic. Max **40 characters**. In range mode, accepts `{"start-date": string, "end-date": string}`. |
| `CP-003` | `mode` | `[OPTIONAL]` Enum: `single` (default) \| `range`. Supports dynamic binding. |
| `CP-004` | `title` | `[OPTIONAL]` Dynamic. **Range mode only.** Max **80 characters**. |
| `CP-005` | `description` | `[OPTIONAL]` Dynamic. **Range mode only.** Max **300 characters**. |
| `CP-006` | `helper-text` | `[OPTIONAL]` Dynamic. Max **80 characters**. In range mode accepts `{"start-date": string, "end-date": string}`. |
| `CP-007` | `required` | `[OPTIONAL]` Boolean or dynamic. Default: `false`. In range mode accepts `{"start-date": boolean, "end-date": boolean}`. |
| `CP-008` | `min-date` | `[OPTIONAL]` `"YYYY-MM-DD"` string. Dynamic binding supported. |
| `CP-009` | `max-date` | `[OPTIONAL]` `"YYYY-MM-DD"` string. Dynamic binding supported. |
| `CP-010` | `unavailable-dates` | `[OPTIONAL]` Array of `"YYYY-MM-DD"` strings. Must fall within min/max range if specified. |
| `CP-011` | `include-days` | `[OPTIONAL]` Array of day names: `["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]`. Default: all 7 days. |
| `CP-012` | `min-days` | `[OPTIONAL]` Integer. **Range mode only.** Minimum days between start and end date. |
| `CP-013` | `max-days` | `[OPTIONAL]` Integer. **Range mode only.** Maximum days between start and end date. |
| `CP-014` | `on-select-action` | `[OPTIONAL]` **Only `data_exchange` is supported.** Payload format: `"YYYY-MM-DD"` (single mode) or `{"start-date":"YYYY-MM-DD","end-date":"YYYY-MM-DD"}` (range mode). |
| `CP-015` | `init-value` | `[OPTIONAL]` Outside Form only. In range mode: `{"start-date": string, "end-date": string}`. |
| `CP-016` | `error-message` | `[OPTIONAL]` Dynamic. Max **80 characters**. Outside Form only. In range mode: `{"start-date": string, "end-date": string}`. |
| `CP-017` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `CP-018` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

### 4.9 ChipsSelector

**Type string:** `"ChipsSelector"` — **Minimum version: v6.3**

| Rule ID | Property | Rule |
|---------|----------|------|
| `CS-001` | `name` | **Required.** Unique string on the screen. |
| `CS-002` | `label` | **Required.** Dynamic. Max **80 characters**. |
| `CS-003` | `data-source` | **Required.** Array of option objects or dynamic binding. Min **2** items. Max **20** items. |
| `CS-004` | `data-source` item shape | Each item: `{ "id": string, "title": string, "enabled": boolean }`. Also accepts: `on-select-action` (`update_data`), `on-unselect-action` (`update_data`). |
| `CS-005` | `min-selected-items` | `[OPTIONAL]` Integer. Dynamic binding supported. |
| `CS-006` | `max-selected-items` | `[OPTIONAL]` Integer. Dynamic binding supported. |
| `CS-007` | `required` | `[OPTIONAL]` Boolean. Dynamic binding supported. |
| `CS-008` | `enabled` | `[OPTIONAL]` Boolean or dynamic. |
| `CS-009` | `description` | `[OPTIONAL]` Dynamic. Max **300 characters**. |
| `CS-010` | `on-select-action` | `[OPTIONAL]` Allowed: `data_exchange` or `update_data` (**update_data requires v7.1+**). |
| `CS-011` | `on-unselect-action` | `[OPTIONAL]` **Requires v7.1+**. Only `update_data` allowed. Same event-splitting behaviour as CheckboxGroup. |
| `CS-012` | `init-value` | `[OPTIONAL]` Array\<string\>. Outside Form only. |
| `CS-013` | `error-message` | `[OPTIONAL]` Dynamic string. Outside Form only. |
| `CS-014` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

## SECTION 5 — INTERACTIVE / NAVIGATION COMPONENTS

### 5.1 Footer

**Type string:** `"Footer"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `FT-001` | `label` | **Required.** Dynamic. Max **35 characters**. |
| `FT-002` | `on-click-action` | **Required.** Must be a valid action object (`navigate`, `complete`, `data_exchange`, `update_data`, `open_url`). |
| `FT-003` | `on-click-action` terminal rule | On a terminal screen Footer, MUST use `complete`. NEVER use `navigate` on a terminal Footer. |
| `FT-004` | `left-caption` | `[OPTIONAL]` Dynamic. Max **15 characters**. |
| `FT-005` | `right-caption` | `[OPTIONAL]` Dynamic. Max **15 characters**. |
| `FT-006` | `center-caption` | `[OPTIONAL]` Dynamic. Max **15 characters**. |
| `FT-007` | Caption exclusivity | `center-caption` CANNOT be set alongside `left-caption` or `right-caption`. Use either center-caption alone OR left+right captions. NOT all three. |
| `FT-008` | `enabled` | `[OPTIONAL]` Boolean or dynamic. |
| `FT-009` | Screen limit | Exactly **1** Footer per screen. No more, no less (on terminal screens). |
| `FT-010` | `If` branch rule | See cross-component rule `X-006`: Footer inside `If` must be in both `then` and `else`. |

---

### 5.2 EmbeddedLink

**Type string:** `"EmbeddedLink"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `EL-001` | `text` | **Required.** Dynamic. Max **25 characters**. Cannot be blank. |
| `EL-002` | `on-click-action` | **Required.** Allowed: `data_exchange`, `navigate`. `open_url` also allowed from **v6.0+**. |
| `EL-003` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `EL-004` | Screen limit | Max **2** EmbeddedLink components per screen (cross-ref `X-011`). |

---

### 5.3 NavigationList

**Type string:** `"NavigationList"` — **Minimum version: v6.2**

| Rule ID | Property | Rule |
|---------|----------|------|
| `NL-001` | `name` | **Required.** Unique string on the screen. |
| `NL-002` | `list-items` | **Required.** Array of item objects or dynamic binding. Min **1** item. Max **20** items. |
| `NL-003` | `on-click-action` (component-level) | `[OPTIONAL]` Allowed: `data_exchange`, `navigate`. Applies the same action to ALL items. |
| `NL-004` | `on-click-action` (item-level) | `[OPTIONAL]` Defined per item for different actions per item. |
| `NL-005` | `on-click-action` exclusivity | MUST be defined at **either** component-level OR item-level — **never both**. |
| `NL-006` | `label` | `[OPTIONAL]` Dynamic. Max **80 characters**. Content truncates at limit. |
| `NL-007` | `description` | `[OPTIONAL]` Dynamic. Max **300 characters**. Content truncates at limit. |
| `NL-008` | `media-size` | `[OPTIONAL]` Enum: `regular` (default) \| `large`. Dynamic binding supported. |
| `NL-009` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `NL-010` | Screen exclusivity | NavigationList screens MUST NOT contain any other component types (cross-ref `X-004`). |
| `NL-011` | Terminal screen | NavigationList MUST NOT be used on a terminal screen (cross-ref `X-015`). |
| `NL-012` | Screen limit | Max **2** NavigationList components per screen (cross-ref `X-012`). |
| `NL-013` | `badge` limit | Max **1** item in a NavigationList may have a `badge` property. |
| `NL-014` | `end` + `media-size: large` | `end` add-on CANNOT be used when `media-size` is set to `large`. |
| `NL-015` | Item `main-content.title` | **Required** on each item. Max **30 characters**. |
| `NL-016` | Item `main-content.description` | `[OPTIONAL]` Max **20 characters**. |
| `NL-017` | Item `main-content.metadata` | `[OPTIONAL]` Max **80 characters**. |
| `NL-018` | Item `start.image` | **Required** within `start` object. Base64 encoded. Max **100 KB**. WEBP requires iOS 14+. |
| `NL-019` | Item `end.title/description/metadata` | `[OPTIONAL]` Each max **10 characters**. |
| `NL-020` | Item `badge` | `[OPTIONAL]` Max **15 characters**. |
| `NL-021` | Item `tags` | `[OPTIONAL]` Max **3** tags per item. Each tag max **15 characters**. |

---

## SECTION 6 — DISPLAY COMPONENTS

### 6.1 Image

**Type string:** `"Image"`

| Rule ID | Property | Rule |
|---------|----------|------|
| `IM-001` | `src` | **Required.** Base64-encoded image string. Supports dynamic binding. |
| `IM-002` | Supported formats | JPEG and PNG only. |
| `IM-003` | Recommended size | Max **300 KB** per image. |
| `IM-004` | `width` | `[OPTIONAL]` Integer. Supports dynamic binding. |
| `IM-005` | `height` | `[OPTIONAL]` Integer. Supports dynamic binding. |
| `IM-006` | `scale-type` | `[OPTIONAL]` Enum: `contain` (default) \| `cover`. |
| `IM-007` | `scale-type: contain` Android | On Android, if no `height` is specified, WhatsApp sets a default height of 400 which may add unwanted whitespace. Set explicit `height` when using `contain`. |
| `IM-008` | `scale-type: cover` | Image is clipped to fill the container. If `height` is not set, image renders at full width with original aspect ratio. |
| `IM-009` | `aspect-ratio` | `[OPTIONAL]` Number. Default: `1`. Supports dynamic binding. |
| `IM-010` | `alt-text` | `[OPTIONAL]` Dynamic string. For accessibility (TalkBack / VoiceOver). |
| `IM-011` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `IM-012` | Screen limit | Max **3** Image components per screen (cross-ref `X-009`). |

---

### 6.2 ImageCarousel

**Type string:** `"ImageCarousel"` — **Minimum version: v7.1**

| Rule ID | Property | Rule |
|---------|----------|------|
| `IC-001` | `images` | **Required.** Array of image objects or dynamic binding. Min **1**. Max **3** images. |
| `IC-002` | Image item `src` | **Required** on each image item. Base64 encoded string. |
| `IC-003` | Image item `alt-text` | **Required** on each image item. String for accessibility. |
| `IC-004` | `aspect-ratio` | `[OPTIONAL]` Enum: `"4:3"` (default) \| `"16:9"`. |
| `IC-005` | `scale-type` | `[OPTIONAL]` Enum: `"contain"` (default) \| `"cover"`. |
| `IC-006` | Screen limit | Max **2** ImageCarousel components per screen (cross-ref `X-013`). |
| `IC-007` | Flow limit | Max **3** ImageCarousel components across the entire Flow (cross-ref `X-014`). |
| `IC-008` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

## SECTION 7 — CONDITIONAL COMPONENTS

### 7.1 If

**Type string:** `"If"` — **Minimum version: v4.0**

| Rule ID | Property | Rule |
|---------|----------|------|
| `IF-001` | `condition` | **Required.** Boolean expression string. |
| `IF-002` | `condition` dynamic requirement | Must contain at least **one** dynamic variable (`${data.*}` or `${form.*}`). Pure static expressions are invalid. |
| `IF-003` | `condition` type requirement | Must **always resolve to boolean**. String or number expressions alone are invalid. |
| `IF-004` | `then` | **Required.** Array of component objects. Must contain at least **1** component. |
| `IF-005` | `else` | `[OPTIONAL]` unless a `Footer` is in `then` — then `else` is **required** and must also contain a `Footer`. |
| `IF-006` | Nesting depth | `If` components may be nested up to **3 levels** deep. Level 4+ is invalid. |
| `IF-007` | Footer placement | `Footer` may only be inside a **level 1 (outermost)** `If`. Nested `If` components cannot contain `Footer`. |
| `IF-008` | Footer symmetry | `Footer` must appear in **both** `then` and `else`, or in **neither**. |
| `IF-009` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `IF-010` | Condition operators | Supported: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `\|\|`, `!`, `()`. |
| `IF-011` | Allowed children | `TextHeading`, `TextSubheading`, `TextBody`, `TextCaption`, `CheckboxGroup`, `DatePicker`, `Dropdown`, `EmbeddedLink`, `Footer`, `Image`, `OptIn`, `RadioButtonsGroup`, `Switch`, `TextArea`, `TextInput`, `If` (nested). From **v7.1**: `ChipsSelector` also allowed. |

---

### 7.2 Switch

**Type string:** `"Switch"` — **Minimum version: v4.0**

| Rule ID | Property | Rule |
|---------|----------|------|
| `SW-001` | `value` | **Required.** Dynamic variable string to evaluate (e.g. `"${data.plan_type}"`). |
| `SW-002` | `cases` | **Required.** Object mapping string keys → Array\<Component\>. Must contain at least **1** key. Empty `{}` is invalid. |
| `SW-003` | `cases` children | Same allowed component types as `If` (see `IF-011`). |
| `SW-004` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |

---

## SECTION 8 — MEDIA UPLOAD COMPONENTS

> ⚠️ **Cloud API only.** Not supported by On-Premise API.
> ⚠️ `PhotoPicker` and `DocumentPicker` are **mutually exclusive** per screen (cross-ref `X-003`).

### 8.1 PhotoPicker

**Type string:** `"PhotoPicker"` — **Minimum version: v4.0**

| Rule ID | Property | Rule |
|---------|----------|------|
| `PP-001` | `name` | **Required.** Unique string on the screen. |
| `PP-002` | `label` | **Required.** Dynamic. Max **80 characters**. |
| `PP-003` | `description` | `[OPTIONAL]` Dynamic. Max **300 characters**. |
| `PP-004` | `photo-source` | `[OPTIONAL]` Enum: `camera_gallery` (default) \| `camera` \| `gallery`. |
| `PP-005` | `max-file-size-kb` | `[OPTIONAL]` Integer. Default: **25600** (25 MiB). Range: **1–25600**. |
| `PP-006` | `min-uploaded-photos` | `[OPTIONAL]` Integer. Default: **0** (optional upload). Range: **0–30**. Set >0 to make upload required. |
| `PP-007` | `max-uploaded-photos` | `[OPTIONAL]` Integer. Default: **30**. Range: **1–30**. MUST be ≥ `min-uploaded-photos`. |
| `PP-008` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `PP-009` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `PP-010` | `error-message` | `[OPTIONAL]` String (generic error) or Object `{"media_id": "error_message"}` for per-file errors. Dynamic binding supported. |
| `PP-011` | `init-values` | NOT supported. PhotoPicker CANNOT be pre-populated via Form `init-values`. |
| `PP-012` | Screen limit | Max **1** PhotoPicker per screen (cross-ref `X-003`). |
| `PP-013` | `navigate` payload | PhotoPicker value MUST NOT appear in a `navigate` action payload. Use Global Dynamic Reference `${screen.ID.form.field}` to access it from another screen. |
| `PP-014` | Payload nesting | In `data_exchange` or `complete` payload, PhotoPicker value MUST be a **top-level key** only. Nested inside an object is INVALID. ✅ `"payload": { "media": "${form.photo}" }` ❌ `"payload": { "wrapper": { "media": "${form.photo}" } }` |
| `PP-015` | Response message limit | When media is sent in the response message (not via endpoint): max **10 files**, max **100 MiB** aggregate. |

---

### 8.2 DocumentPicker

**Type string:** `"DocumentPicker"` — **Minimum version: v4.0**

| Rule ID | Property | Rule |
|---------|----------|------|
| `DC-001` | `name` | **Required.** Unique string on the screen. |
| `DC-002` | `label` | **Required.** Dynamic. Max **80 characters**. |
| `DC-003` | `description` | `[OPTIONAL]` Dynamic. Max **300 characters**. |
| `DC-004` | `max-file-size-kb` | `[OPTIONAL]` Integer. Default: **25600** (25 MiB). Range: **1–25600**. |
| `DC-005` | `min-uploaded-documents` | `[OPTIONAL]` Integer. Default: **0**. Range: **0–30**. Set >0 to make upload required. |
| `DC-006` | `max-uploaded-documents` | `[OPTIONAL]` Integer. Default: **30**. Range: **1–30**. MUST be ≥ `min-uploaded-documents`. |
| `DC-007` | `allowed-mime-types` | `[OPTIONAL]` Array\<string\>. Default: all supported MIME types. See full list in Section 8.3. |
| `DC-008` | `enabled` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `DC-009` | `visible` | `[OPTIONAL]` Boolean or dynamic. Default: `true`. |
| `DC-010` | `error-message` | `[OPTIONAL]` String or Object `{"media_id": "error_message"}`. Dynamic binding supported. |
| `DC-011` | `init-values` | NOT supported. DocumentPicker CANNOT be pre-populated via Form `init-values`. |
| `DC-012` | Screen limit | Max **1** DocumentPicker per screen (cross-ref `X-003`). |
| `DC-013` | `navigate` payload | DocumentPicker value MUST NOT appear in a `navigate` action payload. |
| `DC-014` | Payload nesting | Same top-level-only rule as PhotoPicker (`PP-014`). |
| `DC-015` | Response message limit | Max **10 files**, max **100 MiB** aggregate. |

---

### 8.3 Supported MIME Types (DocumentPicker)

| Category | MIME Types |
|----------|-----------|
| Documents | `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Spreadsheets | `application/vnd.ms-excel`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `application/vnd.oasis.opendocument.spreadsheet` |
| Presentations | `application/vnd.ms-powerpoint`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `application/vnd.oasis.opendocument.presentation` |
| Text | `application/vnd.oasis.opendocument.text`, `text/plain` |
| Archives | `application/gzip`, `application/zip`, `application/x-7z-compressed` |
| Images | `image/avif`, `image/gif`, `image/heic`, `image/heif`, `image/jpeg`*, `image/png`, `image/tiff`, `image/webp` |
| Video | `video/mp4`, `video/mpeg` |

> *`image/jpeg` in `allowed-mime-types` additionally enables gallery photo selection.
> Note: Some older Android/iOS versions may not fully enforce MIME type restrictions.

---

## SECTION 9 — VALIDATION CHECKLIST

Before emitting any component or screen, the agent MUST run through this checklist:

### Per-Component Checks
- [ ] `type` property present and correctly spelled?
- [ ] All **Required** properties present?
- [ ] All character limits respected?
- [ ] `name` is unique on this screen (for input components)?
- [ ] Version-gated features: does the Flow's declared `version` meet the minimum?
- [ ] Dynamic bindings use correct syntax (`${data.*}`, `${form.*}`, or global `${screen.*.*.*}`)?
- [ ] No `null` values anywhere?
- [ ] No blank/whitespace-only `text`, `label`, or `name` strings?

### Per-Screen Checks
- [ ] Total components ≤ 50?
- [ ] Exactly 1 Footer (on terminal screens)?
- [ ] No `navigate` action on a terminal screen's Footer?
- [ ] Not mixing PhotoPicker + DocumentPicker?
- [ ] Not mixing NavigationList with other components?
- [ ] RichText screen isolation respected (per version)?
- [ ] Image count ≤ 3?
- [ ] OptIn count ≤ 5?
- [ ] EmbeddedLink count ≤ 2?
- [ ] NavigationList count ≤ 2?
- [ ] ImageCarousel count ≤ 2?
- [ ] If Footer is inside `If`: exists in both branches AND not outside `If`?

### Per-Flow Checks
- [ ] ImageCarousel total ≤ 3 across the Flow?
- [ ] `routing_model` declared if and only if a Data Endpoint is used?
- [ ] `data_channel_uri` absent from v3.0+ documents?
- [ ] All `data` block fields have `__example__`?

---

## SECTION 10 — QUICK PROPERTY LIMITS REFERENCE

| Component | Property | Limit |
|-----------|----------|-------|
| TextHeading | `text` | 80 chars |
| TextSubheading | `text` | 80 chars |
| TextBody | `text` | 4096 chars |
| TextCaption | `text` | 4096 chars |
| TextInput | `label` | 20 chars |
| TextInput | `helper-text` | 80 chars |
| TextInput | `error-message` | 30 chars |
| TextArea | `label` | 20 chars |
| TextArea | `helper-text` | 80 chars |
| TextArea | `max-length` default | 600 chars |
| CheckboxGroup | `label` | 30 chars |
| CheckboxGroup option | `title` | 30 chars |
| CheckboxGroup option | `description` | 300 chars |
| CheckboxGroup option | `metadata` | 20 chars |
| CheckboxGroup option | `image` | 300 KB (< v6.0) / 100 KB (v6.0+) |
| Dropdown | `label` | 20 chars |
| Dropdown option | `title` | 30 chars |
| Dropdown | max options (no images) | 200 |
| Dropdown | max options (with images) | 100 |
| Footer | `label` | 35 chars |
| Footer | `left/right-caption` | 15 chars each |
| Footer | `center-caption` | 15 chars |
| OptIn | `label` | 120 chars |
| EmbeddedLink | `text` | 25 chars |
| DatePicker | `label` | 40 chars |
| DatePicker | `helper-text` | 80 chars |
| DatePicker | `error-message` | 80 chars |
| CalendarPicker | `title` | 80 chars |
| CalendarPicker | `description` | 300 chars |
| CalendarPicker | `label` | 40 chars |
| CalendarPicker | `helper-text` | 80 chars |
| CalendarPicker | `error-message` | 80 chars |
| ChipsSelector | `label` | 80 chars |
| ChipsSelector | `description` | 300 chars |
| ChipsSelector | min options | 2 |
| ChipsSelector | max options | 20 |
| NavigationList | `label` | 80 chars |
| NavigationList | `description` | 300 chars |
| NavigationList | min items | 1 |
| NavigationList | max items | 20 |
| NavigationList item | `main-content.title` | 30 chars |
| NavigationList item | `main-content.description` | 20 chars |
| NavigationList item | `main-content.metadata` | 80 chars |
| NavigationList item | `start.image` | 100 KB |
| NavigationList item | `end.title/description/metadata` | 10 chars each |
| NavigationList item | `badge` | 15 chars |
| NavigationList item | `tags` | 3 tags / 15 chars each |
| PhotoPicker | `label` | 80 chars |
| PhotoPicker | `description` | 300 chars |
| PhotoPicker | `max-file-size-kb` | 1–25600 |
| PhotoPicker | `min/max-uploaded-photos` | 0–30 / 1–30 |
| DocumentPicker | `label` | 80 chars |
| DocumentPicker | `description` | 300 chars |
| DocumentPicker | `max-file-size-kb` | 1–25600 |
| DocumentPicker | `min/max-uploaded-documents` | 0–30 / 1–30 |
| ImageCarousel | images per carousel | 1–3 |
| ImageCarousel | carousels per screen | 2 |
| ImageCarousel | carousels per Flow | 3 |

---

*This ruleset is authoritative for the `whatsapp-flows` skill.*
*Source: Meta for Developers — /reference/components | /reference/flowjson | /reference/media_upload*