## 📚 Simulation Reference: Pendo Workflow Assistant

This reference supplements the main assistant instructions with **advanced examples**, **Playwright action patterns**, and **tips for robust simulations**.

---

### 🎬 Reliable Interaction Patterns

#### ✅ Dropdown Interactions (CRITICAL)

**Always use two steps**: open dropdown first, then select by visible text.

```json
{"action": "click", "selector": "[data-pendo-id='integration-type-dropdown']", "delay_ms": 600, "description": "Open dropdown"},
{"action": "click", "selector": "text='Payment Processing'", "delay_ms": 700, "description": "Select Payment Processing"}
```

**Dropdown Option Selector Strategy (in order):**

1. `text='Option Label'`
2. `role=option >> text='Label'`
3. `[data-value='value']`
4. `[data-pendo-id*='label']`
5. `.class >> text='Label'`

---

### 📥 Form Inputs

```json
{"action": "type", "selector": "[data-pendo-id='api-key-input']", "value": "prod-123", "delay_ms": 800, "description": "Enter API Key"}
```

---

### 🖱️ Click Events

- Use stable selectors: `data-pendo-id`, `data-testid`, `id`
- Add 500–1200ms delays to mimic natural flow

```json
{"action": "click", "selector": "[data-pendo-id='next-step-btn']", "delay_ms": 700, "description": "Go to next step"}
```

---

### ⏳ Wait Actions

- Use for pauses or when user reads/evaluates content

```json
{"action": "wait", "delay_ms": 4000, "description": "User pauses before continuing"}
```

---

### 🧭 Navigation

```json
{"action": "navigate", "value": "/dashboard", "delay_ms": 1200, "description": "Start at dashboard"}
```

---

### 💡 Tips for Realism

- Simulate indecision with extra waits
- Use short sequences for drop-off paths
- Include search, dropdowns, and form entry in longer paths
- Reuse common nav elements (e.g., header, nav bar, back button)

---

### 🧪 Example: Feature Configuration Path

```json
{
  "path_id": "feature_config_path",
  "percentage": 20.0,
  "description": "User configures an integration feature",
  "steps": [
    {"action": "navigate", "value": "/integrations", "delay_ms": 1600, "description": "Open integrations"},
    {"action": "click", "selector": "[data-pendo-id='integration-card-payments']", "delay_ms": 1100, "description": "Select Payments"},
    {"action": "click", "selector": "[data-pendo-id='integration-type-dropdown']", "delay_ms": 600, "description": "Open dropdown"},
    {"action": "click", "selector": "text='Payment Processing'", "delay_ms": 700, "description": "Choose option"},
    {"action": "click", "selector": "[data-pendo-id='wizard-next-button']", "delay_ms": 800, "description": "Continue"},
    {"action": "click", "selector": "[data-pendo-id='environment-dropdown']", "delay_ms": 600, "description": "Open environment"},
    {"action": "click", "selector": "text='Production'", "delay_ms": 800, "description": "Select Production"},
    {"action": "type", "selector": "[data-pendo-id='api-key-input']", "value": "prod-key-123", "delay_ms": 900, "description": "Enter API Key"},
    {"action": "click", "selector": "[data-pendo-id='submit-btn']", "delay_ms": 1100, "description": "Submit configuration"}
  ]
}
```

---

### 🚫 What NOT to Do

```json
// ❌ BAD - option won't be visible until dropdown is open
{"action": "click", "selector": "[data-pendo-id='integration-option-payment-processing']"}

// ✅ GOOD
{"action": "click", "selector": "[data-pendo-id='integration-type-dropdown']"},
{"action": "click", "selector": "text='Payment Processing'"}
```

---

### 📊 Suggested Path Templates

| Path Type            | Description                   | % Range |
| -------------------- | ----------------------------- | ------- |
| complete\_journey    | Full successful flow          | 12–18%  |
| quick\_exit          | Exits after brief session     | 20–30%  |
| comparison\_behavior | Navigates multiple options    | 25–35%  |
| cart\_abandonment    | Begins flow, exits late       | 15–25%  |
| feature\_exploration | Uses features, doesn't finish | 10–20%  |

---

This reference evolves with usage. Add more patterns, issues, or improvements as needed!

---

### 📋 Complete User Journey Workflow JSON Format

Generate workflows with specific user journey paths in this exact format:

```json
{
  "workflow_name": "ecommerce_product_discovery",
  "description": "Customer product discovery and purchase behavior",
  "user_journey_paths": [
    {
      "path_id": "complete_purchase_path",
      "percentage": 15.0,
      "description": "User completes full purchase journey",
      "steps": [
        {
          "action": "navigate",
          "value": "/",
          "delay_ms": 1500,
          "description": "Start at homepage"
        },
        {
          "action": "type", 
          "selector": "data-pendo-id='search-input'",
          "value": "wireless headphones",
          "delay_ms": 2800,
          "description": "Search for product"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='search-btn'",
          "delay_ms": 1200,
          "description": "Submit search"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='product-card-1'",
          "delay_ms": 2100,
          "description": "Select first product"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='add-to-cart-btn'",
          "delay_ms": 1800,
          "description": "Add to cart"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='checkout-btn'",
          "delay_ms": 1400,
          "description": "Proceed to checkout"
        },
        {
          "action": "type",
          "selector": "data-pendo-id='email-input'",
          "value": "customer@example.com",
          "delay_ms": 4200,
          "description": "Enter email"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='submit-order-btn'",
          "delay_ms": 2100,
          "description": "Complete purchase"
        }
      ]
    },
    {
      "path_id": "cart_abandonment_path",
      "percentage": 28.0,
      "description": "User adds to cart but abandons at checkout",
      "steps": [
        {
          "action": "navigate",
          "value": "/",
          "delay_ms": 1800,
          "description": "Start at homepage"
        },
        {
          "action": "type",
          "selector": "data-pendo-id='search-input'",
          "value": "bluetooth speaker", 
          "delay_ms": 3100,
          "description": "Search for different product"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='search-btn'",
          "delay_ms": 1100,
          "description": "Submit search"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='product-card-2'",
          "delay_ms": 2400,
          "description": "Select product"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='add-to-cart-btn'",
          "delay_ms": 1600,
          "description": "Add to cart"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='view-cart-btn'",
          "delay_ms": 2800,
          "description": "View cart contents"
        },
        {
          "action": "wait",
          "delay_ms": 8000,
          "description": "User hesitates and exits"
        }
      ]
    },
    {
      "path_id": "comparison_shopping_path",
      "percentage": 35.0,
      "description": "User compares multiple products",
      "steps": [
        {
          "action": "navigate",
          "value": "/",
          "delay_ms": 1600,
          "description": "Start at homepage"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='browse-products-btn'",
          "delay_ms": 2200,
          "description": "Browse all products"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='product-card-1'",
          "delay_ms": 2200,
          "description": "View first product"
        },
        {
          "action": "navigate",
          "value": "/products",
          "delay_ms": 3400,
          "description": "Return to product list"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='product-card-3'",
          "delay_ms": 2600,
          "description": "Compare with different product"
        },
        {
          "action": "wait",
          "delay_ms": 4000,
          "description": "User leaves without purchasing"
        }
      ]
    },
    {
      "path_id": "quick_exit_path",
      "percentage": 22.0,
      "description": "User exits quickly after brief look",
      "steps": [
        {
          "action": "navigate",
          "value": "/",
          "delay_ms": 1200,
          "description": "Land on homepage"
        },
        {
          "action": "click",
          "selector": "data-pendo-id='browse-products-btn'",
          "delay_ms": 2800,
          "description": "Quick browse attempt"
        },
        {
          "action": "wait",
          "delay_ms": 3500,
          "description": "User exits immediately"
        }
      ]
    }
  ],
  "metadata": {
    "total_paths": 4,
    "estimated_avg_duration_ms": 95000,
    "focus": "purchase_funnel_analysis"
  }
}
```

---

### 🎯 Advanced Click Event Capture Tips

- **4+ clicks per path**: More interactions = better event batching
- **Keep delays ≤ 800ms**: Fast sequences trigger Pendo's natural batching  
- **Use common elements**: Header nav, logos, footers usually exist and work well

---

### 🧠 Behavioral Realism Guidelines

- **Product Analytics Focus**: Generate insights about user adoption, feature discovery, and process completion
- **Friction Point Discovery**: Design simulations that reveal where users get stuck or need guidance
- **Adoption Insights**: Focus on feature usage, process efficiency, and user journey optimization

---

