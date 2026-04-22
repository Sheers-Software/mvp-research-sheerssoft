# NOCTURN AI — BRANDING & DESIGN SYSTEM 

**Version 1.0 — April 2026**  
**Optimized for Product-Led Growth (PLG)**  

---

## 1. STRATEGIC POSITIONING
Nocturn AI is the premium revenue recovery layer for high-end hospitality. The brand identity balances **24/7 reliability** (The Nocturn Crescent) with **modern enterprise trust** (Midnight Navy & Recovery Green).

---

## 2. LOGO SYSTEM

### 2.1 The Brand Mark
The Nocturn crescent represents the "Midnight Economy"—capturing revenue while typical operations are offline. 
- **Standalone Asset**: `brand/logo.svg`
- **Component**: `brand/Logo.tsx`

### 2.2 Color Variants
| Context | Icon Color | Text Color |
| :--- | :--- | :--- |
| **Light BG (Standard)** | `#0F172A` (Navy) | `#0F172A` (Navy) |
| **Dark BG (Hero/Footer)** | `#FFFFFF` (White) | `#FFFFFF` (White) |
| **Accent BG (Gradient)** | `#22C55E` (Green) | `#FFFFFF` (White) |

---

## 3. COLOR PALETTE

### 3.1 Primary Colors (PLG Triggers)
| Color | Hex Code | Variable | Usage |
| :--- | :--- | :--- | :--- |
| **Recovery Green** | `#22C55E` | `--color-green` | Primary CTAs, Success States, "Active" indicators. |
| **Forest Tint** | `#F0FDF4` | `--color-green-light` | Hover states, subtle secondary backgrounds. |
| **Midnight Navy** | `#0F172A` | `--color-navy` | Main typography, Headers, Primary interface contrast. |

### 3.2 Premium Elements
- **Rainbow Gradient**: `linear-gradient(90deg, #ff00cc, #3333ff, #00d4ff)` — Used for spotlighting breakthrough features.
- **Glassmorphism**: `backdrop-filter: blur(12px);` — Used for modern dashboard overlays.

---

## 4. TYPOGRAPHY

### 4.1 Typeface Selection
- **Display Typography**: **`Instrument Serif`** (700+)  
  *Usage*: Hero headlines, brand statements, premium case studies.
- **Interface Typography**: **`Inter`** (300, 400, 600, 700)  
  *Usage*: Navigation, body text, form fields, and functional product UI.

### 4.2 Type Scale
- **Hero Title**: `clamp(3rem, 8vw, 6rem)` (900 weight)
- **H2 Headline**: `clamp(2rem, 5vw, 3.5rem)` (700 weight)
- **Body Text**: `1rem` (400 weight, 1.6 line-height)
- **Eyebrow Label**: `0.75rem` (Uppercase, 2px letter-spacing)

---

## 5. UI STYLE & COMPONENTS

### 5.1 Buttons
- **Shape**: Fully rounded pill shape (`border-radius: 100px`).
- **Primary Style**: Recovery Green background with `--shadow-neon`.
- **Secondary Style**: Navy outline or solid white for dark mode contexts.

### 5.2 Layout & Spacing
- **Container Max-Width**: `1200px`.
- **Vertical Spacing**: High-breathability sections using `clamp(100px, 15vw, 180px)` padding.

---

## 6. ASSET REUSE
To maintain brand alignment across new products or sub-domains:
1.  **Inject Tokens**: Reference [`brand/theme.css`](./theme.css).
2.  **Mount Logo**: Implement [`brand/Logo.tsx`](./Logo.tsx).
3.  **Follow PLG Rules**: Prioritize the Recovery Green for all "Aha!" moments in the product flow.
