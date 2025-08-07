# Lovable Instructions: Generate Pendo Workflow README

## Instructions for Lovable

Please create a comprehensive README.md file that documents this application for Pendo workflow simulation. The README should include:

### 1. App Overview
```markdown
# [App Name] - Pendo Workflow Documentation

## App Type & Purpose
- **App Type**: [e.g., E-commerce, SaaS Dashboard, Social Media]
- **Primary Purpose**: [Brief description]
- **Target Users**: [Who uses this app]

## Business Workflows
[List 2-4 main user workflows/journeys]
```

### 2. UI Elements & Selectors
Comprehensive inventory of ALL interactive elements with exact selectors:

```markdown
## UI Elements & Selectors

### Navigation Elements
| Element | Selector | Description | Page/Component |
|---------|----------|-------------|----------------|
| Home Button | `[data-pendo-id='nav-home']` | Main navigation home | Header |
| Profile Menu | `[data-pendo-id='profile-menu']` | User profile dropdown | Header |

### Form Elements  
| Element | Selector | Description | Page/Component |
|---------|----------|-------------|----------------|
| Email Input | `[data-pendo-id='email-input']` | User email field | Login/Signup |
| Submit Button | `[data-pendo-id='submit-btn']` | Form submission | Multiple |

### Interactive Components
| Element | Selector | Description | Page/Component |
|---------|----------|-------------|----------------|
| Product Card | `[data-pendo-id='product-card']` | Individual product | Product List |
| Add to Cart | `[data-pendo-id='add-cart-btn']` | Add item to cart | Product Detail |

### Dropdown Elements
| Element | Selector | Description | Options Available |
|---------|----------|-------------|-------------------|
| Category Filter | `[data-pendo-id='category-dropdown']` | Product category selection | Electronics, Clothing, Books |
| Sort Options | `[data-pendo-id='sort-dropdown']` | Product sorting | Price: Low to High, Newest First |
```

### 3. User Journey Workflows
Step-by-step workflow documentation:

```markdown
## Detailed User Journey Workflows

### Workflow 1: [Name] (e.g., Product Purchase Journey)
**Description**: [What this workflow accomplishes]
**Success Criteria**: [How to know the workflow completed successfully]

**Steps**:
1. **Start**: Navigate to homepage (`/`)
2. **Browse**: Click category filter `[data-pendo-id='category-dropdown']` → Select "Electronics"
3. **Search**: Type in search box `[data-pendo-id='search-input']` → Click search `[data-pendo-id='search-btn']`
4. **Select**: Click product card `[data-pendo-id='product-card-1']`
5. **Add to Cart**: Click `[data-pendo-id='add-cart-btn']`
6. **Checkout**: Click `[data-pendo-id='checkout-btn']`
7. **Complete**: Fill form fields and submit `[data-pendo-id='complete-order-btn']`

**Alternative Paths**:
- **Quick Exit**: User leaves after step 2 (browsing only)
- **Comparison Shopping**: User views multiple products (steps 1-4, then repeat 4)
- **Cart Abandonment**: User completes steps 1-5 but exits before checkout

### Workflow 2: [Next workflow...]
[Repeat the same detailed format]
```

### 4. Page Structure
```markdown
## Page Structure & Routes

### Available Routes
| Route | Purpose | Key Elements | Main Actions |
|-------|---------|--------------|--------------|
| `/` | Homepage | Hero, navigation, featured items | Browse, search |
| `/products` | Product listing | Filters, product grid | Filter, sort, select |
| `/product/[id]` | Product detail | Images, description, add to cart | View, add to cart |
| `/cart` | Shopping cart | Item list, quantities, checkout | Modify cart, checkout |
| `/checkout` | Order completion | Forms, payment | Complete purchase |

### Key Components
- **Header**: Navigation, search, user menu
- **Product Grid**: Filterable/sortable product display  
- **Product Card**: Individual product preview
- **Cart Component**: Shopping cart management
- **Checkout Form**: Order completion workflow
```

### 5. Technical Notes
```markdown
## Technical Implementation Notes

### Selector Patterns Used
- Primary selectors: `data-pendo-id` attributes
- Fallback selectors: `data-testid`, `id`, or `class` attributes
- Text-based selectors: Available for dropdown options and buttons

### Critical Selector Placement
**CRITICAL**: Place `data-pendo-id` on ACTUAL clickable elements, not wrappers:

#### ✅ CORRECT Examples:
```jsx
// ✅ Good - pendo-id on the clickable SelectTrigger
<Select>
  <SelectTrigger data-pendo-id="integration-type-dropdown">
    <SelectValue />
  </SelectTrigger>
</Select>

// ✅ Good - pendo-id on the actual button element
<div className="button-wrapper">
  <button data-pendo-id="submit-btn">Submit</button>
</div>

// ✅ Good - pendo-id on the input element
<div className="form-group">
  <input data-pendo-id="email-input" type="email" />
</div>
```

#### ❌ INCORRECT Examples:
```jsx
// ❌ Bad - pendo-id on wrapper, not clickable element
<Select data-pendo-id="integration-type-dropdown">
  <SelectTrigger>
    <SelectValue />
  </SelectTrigger>
</Select>

// ❌ Bad - pendo-id on non-interactive wrapper
<div data-pendo-id="submit-btn" className="button-wrapper">
  <button>Submit</button>
</div>
```

### Common Component Issues
- **Select/Dropdown**: Place on `SelectTrigger`, NOT wrapper `Select`
- **Forms**: Place on actual `input`/`textarea`, NOT wrapper divs
- **Buttons**: Ensure pass-through to underlying `<button>` element
- **Modals**: Place on interactive elements, NOT modal wrapper
- **Cards/Lists**: Place on clickable areas, NOT card container

### Form Handling
- All forms use controlled inputs with proper validation
- Submit buttons are disabled until forms are valid
- Error states are clearly indicated with visual feedback
- **Verify**: All form elements have `data-pendo-id` on the actual input elements

### State Management
- [Describe if using React state, Redux, context, etc.]
- [Note any complex state interactions that affect UI]

### Responsive Behavior
- [Note any mobile-specific selectors or behaviors]
- [Mention if certain elements hide/show on different screen sizes]

### Special Interactions
- **Dropdowns**: Require two-step interaction (open dropdown, then select option)
- **Multi-step Forms**: [Describe any wizard-style interfaces]
- **Modal Dialogs**: [List any popup/modal interactions]
- **Conditional Elements**: [Note any elements that only appear after certain actions]
```

**CRITICAL REQUIREMENTS**:

1. **Be Exhaustive**: Include EVERY clickable element, form field, button, and interactive component
2. **Use Exact Selectors**: Provide the actual `data-pendo-id`, `data-testid`, or other selectors used in the code
3. **VERIFY SELECTOR PLACEMENT**: Ensure `data-pendo-id` attributes are on the ACTUAL clickable elements, not wrapper components:
   - ✅ `<SelectTrigger data-pendo-id="dropdown">` NOT `<Select data-pendo-id="dropdown">`
   - ✅ `<button data-pendo-id="submit">` NOT `<div data-pendo-id="submit">`
   - ✅ `<input data-pendo-id="email">` NOT `<div data-pendo-id="email">`
4. **Include All Pages**: Document selectors from every page/route in the application
5. **Specify Dropdown Options**: For any dropdown, list all available options that can be selected
6. **Detail Form Fields**: Include every input field with its purpose and validation requirements
7. **Map User Flows**: Connect the UI elements into realistic user journey sequences
8. **Note Dependencies**: Mention if certain elements only appear after other actions (conditional rendering)
9. **Test Interactivity**: Verify that documented selectors actually correspond to clickable/typeable elements

Generate this README with actual data from the current application, not placeholder text. 