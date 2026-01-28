# Pricing Intelligence Matrix

Framework for analyzing and comparing competitor pricing strategies.

## Pricing Model Types

| Model | Description | When Used | Our Position |
|-------|-------------|-----------|--------------|
| **Per-Project** | Fixed price for defined scope | Complex, custom work | Best for high-value clients |
| **Hourly** | Time-based billing | Consulting, ongoing work | Transparent but unpredictable |
| **Package/Tier** | Good/Better/Best options | Productized services | Most scalable |
| **Value-Based** | Price tied to outcomes | High ROI services | Premium positioning |
| **Subscription** | Recurring monthly/annual | Ongoing services | Predictable revenue |

## Price Positioning Grid

```
                    HIGH PRICE
                        |
        Premium         |        Value Trap
        (High value,    |        (High price,
         justified)     |         low perceived value)
                        |
 LOW VALUE -------------|------------- HIGH VALUE
                        |
        Budget          |        Value Leader
        (Low price,     |        (High value,
         low value)     |         competitive price)
                        |
                    LOW PRICE
```

## Competitor Price Capture Template

```yaml
competitor:
  name: "[Name]"
  url: "[pricing page URL]"
  captured_date: "[YYYY-MM-DD]"

pricing_model: "[per-project | hourly | package | value | subscription]"

packages:
  - name: "Basic"
    price: "$X"
    price_type: "one-time | monthly | per-project"
    features:
      - "Feature 1"
      - "Feature 2"
    limitations:
      - "Up to X [units]"
    best_for: "[customer type]"

  - name: "Professional"
    price: "$Y"
    features:
      - "Everything in Basic"
      - "Feature 3"
    highlighted: true  # If marked as "most popular"

add_ons:
  - name: "Add-on Service"
    price: "$Z"
    notes: "Optional extra"

custom_pricing:
  available: true
  triggers: "Enterprise, 10+ locations, special requirements"
  cta: "Contact for quote"

hidden_costs:
  - "Setup fee ($X)"
  - "Hosting ($X/month)"
  - "Rush delivery (+50%)"

price_anchoring:
  highest_shown: "$X,XXX"
  lowest_shown: "$XXX"
  anchor_technique: "[decoy | contrast | bundle]"
```

## Analysis Checklist

### Price Discovery
- [ ] Main pricing page found
- [ ] All tiers documented
- [ ] Add-ons captured
- [ ] Hidden costs identified
- [ ] Custom pricing process noted

### Positioning Analysis
- [ ] What quadrant are they in? (Premium/Budget/Value)
- [ ] How do they anchor price?
- [ ] What's included vs. extra?
- [ ] How do they justify premium?

### Competitive Response
- [ ] Are we priced above/below/at market?
- [ ] What's our value differentiation?
- [ ] Where can we win on value?
- [ ] Where should we not compete on price?

## Van Westendorp Analysis (Advanced)

If you can survey customers:

1. **Too Cheap**: Below what price would you question quality?
2. **Cheap/Good Value**: What price is a good deal?
3. **Expensive/Still Consider**: What price is getting expensive but still acceptable?
4. **Too Expensive**: What price is too high to consider?

Plot responses to find:
- **Point of Marginal Cheapness (PMC)**: Minimum viable price
- **Point of Marginal Expensiveness (PME)**: Maximum price
- **Optimal Price Point (OPP)**: Where resistance is lowest
- **Indifference Price Point (IDP)**: Market equilibrium

## Decision Framework

### Price ABOVE competitor when:
- You have demonstrably better quality
- Your local reputation is stronger
- You offer meaningful differentiators
- Target audience values premium

### Price AT competitor when:
- Services are comparable
- Competing on other factors
- Market is price-sensitive
- Building market share

### Price BELOW competitor when:
- Entering new market
- Volume strategy
- Competitor has quality issues
- Disrupting with efficiency

---

_Last updated: Include date when using_
_Related: /pricing_intel for deep price research_
