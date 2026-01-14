# Dashboard Enhancements Design

## Overview

Five UI enhancements for the Vamana stock market dashboard:

1. Dark/Light theme toggle
2. Simplified sector/industry/basic industry cards with RSI sorting
3. Stock list below charts
4. Bold RSI reference lines with zone shading
5. Logarithmic scale toggle for price charts

---

## 1. Theme Toggle (Dark/Light Mode)

### Implementation

**Toggle button location:** Header navigation bar, top-right corner

**Button design:**
- Sun icon (light mode active) / Moon icon (dark mode active)
- Click to switch themes instantly

**Theme configuration:**

```javascript
const themes = {
  dark: {
    layout: { background: { color: '#131722' }, textColor: '#d1d4dc' },
    grid: { vertLines: { color: '#363a45' }, horzLines: { color: '#363a45' } },
    borderColor: '#363a45'
  },
  light: {
    layout: { background: { color: '#ffffff' }, textColor: '#191919' },
    grid: { vertLines: { color: '#e1e1e1' }, horzLines: { color: '#e1e1e1' } },
    borderColor: '#e1e1e1'
  }
};
```

**Chart theme switching:**
- Use `chart.applyOptions()` to update colors dynamically
- Update both candlestick and RSI chart instances
- Update scale borders via `chart.priceScale().applyOptions()` and `chart.timeScale().applyOptions()`

**CSS theme switching:**
- Toggle `data-theme="light"` attribute on `<html>` element
- Define light theme CSS variables under `[data-theme="light"]` selector

**Light theme CSS variables:**
```css
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #e8e8e8;
  --text-primary: #191919;
  --text-secondary: #6b6b6b;
  --border-color: #e1e1e1;
  /* Keep accent colors same for consistency */
}
```

**Persistence:**
- Save preference to `localStorage` key: `vamana-theme`
- On page load, apply saved theme (default: dark)

---

## 2. Simplified Sector/Industry/Basic Industry Cards

### Current State (to remove)
- Company count ("24 Companies")
- Company name previews ("TCS, Infosys, Wipro...")
- Chart icon (top-right)

### New Card Design

```
┌────────────────────────────────────────┐
│                                        │
│           Technology                   │  ← Name (medium weight)
│                                        │
│              58.3                      │  ← RSI value (large, bold, colored)
│           ━━━━━━━━━━                   │  ← RSI progress bar (0-100 scale)
│                                        │
└────────────────────────────────────────┘
```

### Professional Styling

**RSI progress bar:**
- Thin horizontal bar showing RSI position on 0-100 scale
- Bar fills from left based on RSI value
- Color: green (≤40) → orange (40-60) → red (≥60)

**Typography:**
- Name: 14-16px, medium weight
- RSI: 24-28px, bold

**RSI value coloring:**
- `#ef5350` (red) if RSI ≥ 60
- `#26a69a` (green) if RSI ≤ 40
- `#787b86` (neutral gray) if 40-60

**Card styling:**
- Subtle border, slight rounded corners (8px)
- Clean hover: subtle border highlight
- Consistent padding

**Sorting:**
- All cards sorted descending by RSI value (highest first)

**Affected tabs:**
- Sectors
- Industries
- Basic Industries
- RSI filter tabs (above 65, 50-65, below 40)

---

## 3. Stock List Below Charts

### Location
Below the RSI chart in the chart view

### Design

```
┌──────────────────────────────────────────────────────┐
│  Stocks in Technology                          (12)  │  ← Header with count
├──────────────────────────────────────────────────────┤
│  TCS                                           72.4  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
├──────────────────────────────────────────────────────┤
│  Infosys                                       68.1  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━        │
├──────────────────────────────────────────────────────┤
│  Wipro                                         54.2  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              │
└──────────────────────────────────────────────────────┘
```

### Features

**Content per row:**
- Stock name (left-aligned)
- RSI value (right-aligned, colored by zone)
- RSI progress bar (same style as cards)

**Sorting:** Descending by RSI value

**Styling:**
- Matches current theme (dark/light)
- Subtle row separators
- Compact but readable
- Scrollable container (max-height ~300px)

**Data source:**
- Filter `symbolData` by current sector/industry/basic_industry
- Fetch individual stock RSI values from API

---

## 4. Bold RSI 40 and 60 Lines with Zone Shading

### Current State
- Lines at 40 and 65
- Semi-transparent colors (`rgba(..., 0.5)`)
- Dashed style, 1px width

### New Design

**Line changes:**
- Values: 40 (lower) and 60 (upper) — changed from 65
- Width: 2px (up from 1px)
- Style: Solid (changed from dashed)
- Colors: Full opacity
  - 40 line: `#26a69a` (solid green)
  - 60 line: `#ef5350` (solid red)

**Zone shading:**
- Light red tint above 60 line (overbought zone)
- Light green tint below 40 line (oversold zone)
- Implementation: Use area series or background bands if supported, otherwise CSS overlay

---

## 5. Logarithmic Scale Toggle

### Location
Legend area, next to OHLC values

### Design

```
┌─────────────────────────────────────────────────────────────┐
│  Technology                                                 │
│  O: 1245.50  H: 1280.00  L: 1220.00  C: 1265.75   [LOG]    │
└─────────────────────────────────────────────────────────────┘
```

### Button Behavior

**Appearance:**
- Small pill-shaped button
- Text: `LIN` or `LOG`
- Active state: filled background
- Inactive state: outline only

**Functionality:**
- Click toggles between linear and logarithmic
- API: `chart.priceScale('right').applyOptions({ mode: 0 })` for linear
- API: `chart.priceScale('right').applyOptions({ mode: 1 })` for logarithmic
- Only affects price chart, not RSI chart

**Persistence:**
- Save to `localStorage` key: `vamana-scale-mode`
- Apply on chart load (default: linear)

---

## Files to Modify

1. **index.html** - Main file containing:
   - CSS variables and styles
   - HTML structure (header, cards, chart view)
   - JavaScript (chart creation, data loading, rendering)

2. **js/db-client.js** - May need to add method for fetching individual stock RSI values

---

## Implementation Order

1. Theme toggle (foundational - affects all other components)
2. RSI lines and zone shading (isolated change)
3. Log scale toggle (isolated change)
4. Simplified cards with sorting (moderate complexity)
5. Stock list below charts (requires data loading changes)
