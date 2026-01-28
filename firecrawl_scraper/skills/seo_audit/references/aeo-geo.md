# AEO/GEO Optimization Reference

## What is AEO? (Answer Engine Optimization)

Optimization for AI-powered search experiences:
- Google AI Overviews
- Bing Chat / Copilot
- ChatGPT with browsing
- Perplexity AI
- Voice assistants (Alexa, Siri, Google Assistant)

## What is GEO? (Generative Engine Optimization)

Broader optimization for generative AI systems that synthesize answers from multiple sources.

## Key Differences from Traditional SEO

| Aspect | Traditional SEO | AEO/GEO |
|--------|-----------------|---------|
| **Goal** | Rank in results | Be cited in AI answers |
| **Format** | Any content | Structured, direct answers |
| **Length** | Varies | Concise, scannable |
| **Citations** | Links help ranking | Being a cited source |
| **Voice** | Keyword-optimized | Conversational, natural |

## Content Strategies for AEO

### 1. Direct Answer Format
```markdown
## What is a virtual tour?

A virtual tour is an interactive, 360-degree digital experience
that allows viewers to explore a space remotely. Using specialized
cameras and software, virtual tours capture...

Key benefits include:
- Remote viewing capability
- 24/7 accessibility
- Increased engagement
- Reduced in-person visits needed
```

### 2. Question-Based Headers
```markdown
## How much does a virtual tour cost?
## What equipment is used for virtual tours?
## How long does it take to create a virtual tour?
## Are virtual tours worth it for small businesses?
```

### 3. Structured Data for Rich Answers
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How much does a virtual tour cost?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Virtual tour pricing typically ranges from $200-$500 for small spaces to $1,000+ for large commercial properties..."
    }
  }]
}
```

## Local AEO Optimization

### "Near Me" Query Optimization
```
Target queries like:
- "virtual tour company near me"
- "best virtual tours [city]"
- "virtual tour photographers nearby"
```

### Location-Specific Answers
```markdown
## Virtual Tours in Pittsburgh

Pittsburgh businesses looking for virtual tour services have several
options. The best virtual tour providers in the Pittsburgh area offer:

- Matterport 3D scanning
- 360-degree photography
- Drone aerial tours
- Interactive floor plans

Average pricing in the Pittsburgh market ranges from...
```

### Voice Search Optimization
```
Voice queries are:
- Longer (7+ words average)
- Conversational ("Hey Google, who does virtual tours in Pittsburgh?")
- Question-based
- Location-aware

Optimize for:
- Natural language
- Complete answers
- Featured snippet format
- Local intent
```

## Content Structure for AI Parsing

### The "Answer Box" Format
```markdown
**[Question as H2]**

[Direct answer in first 40-50 words]

[Supporting details in bullet points or short paragraphs]

[Evidence/credentials/source attribution]
```

### Example
```markdown
## How long does a virtual tour take to create?

A typical virtual tour takes 2-4 hours to capture and 3-5 business
days to process and deliver. The timeline depends on:

- **Property size**: Small spaces (under 2,000 sq ft) take 1-2 hours
- **Complexity**: Multiple floors or outdoor areas add time
- **Post-production**: Basic tours are faster than fully branded experiences

At Psybir, we've completed over 200 virtual tours in the Pittsburgh
area with an average turnaround of 5 business days.
```

## Source Attribution Signals

AI systems prefer citing sources that:
1. **Have clear expertise** - credentials, experience, authority
2. **Provide unique data** - original research, statistics, case studies
3. **Are recently updated** - fresh content with dates
4. **Have strong E-E-A-T** - established trust signals
5. **Offer comprehensive coverage** - thorough topic exploration

### Building Citation Worthiness
```markdown
## How we establish expertise:

- Include author bylines with credentials
- Link to original research/data
- Reference industry sources
- Update content regularly (show dates)
- Provide comprehensive topic coverage
- Use clear, factual language
```

## Measuring AEO Success

### Metrics to Track
- **AI Overview appearances** (manual checking)
- **Featured snippet wins** (GSC + rank trackers)
- **Voice search visibility** (test with assistants)
- **Brand mentions in AI answers** (monitor tools)
- **Referral traffic from AI sources** (analytics)

### Testing Protocol
```
1. Search target query in Google (logged out, incognito)
2. Check if AI Overview appears
3. If yes, is your content cited?
4. Test same query in:
   - Bing Chat
   - Perplexity
   - ChatGPT (if browsing enabled)
5. Track changes over time
```

## Common AEO Mistakes

1. **Burying the answer** - Lead with direct answer, not context
2. **Over-optimizing** - Write naturally, not robotically
3. **Ignoring structure** - Use headers, lists, tables
4. **Missing schema** - FAQ and HowTo schema help
5. **Outdated content** - AI prefers recent information
6. **No unique value** - Same content as everyone else won't be cited

## Implementation Checklist

### For Each Key Page
- [ ] Identify target questions/queries
- [ ] Lead with direct, concise answer
- [ ] Use question-based H2 headers
- [ ] Implement FAQ schema
- [ ] Add clear expertise signals
- [ ] Include updated date
- [ ] Structure content for scanning
- [ ] Test in AI search tools

### For Local AEO
- [ ] Target "[service] near me" variations
- [ ] Create location-specific content
- [ ] Optimize for voice search length
- [ ] Include local schema markup
- [ ] Build local citations
- [ ] Collect and display reviews

---

_Related: /seo_audit skill, /local_seo, /content_gap_
