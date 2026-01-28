# On-Page SEO Reference

## Title Tag Optimization

### Best Practices
- **Length**: 50-60 characters (520px display width)
- **Structure**: Primary Keyword - Secondary | Brand
- **Uniqueness**: Every page should have unique title
- **Front-load keywords**: Put important words first

### Templates by Page Type
```
Homepage:    [Brand] - [Value Proposition] | [City]
Service:     [Service] in [City] | [Brand] - [Benefit]
Location:    [Service] in [Neighborhood], [City] | [Brand]
Blog:        [Topic]: [Specific Angle] | [Brand]
Product:     [Product Name] - [Key Feature] | [Brand]
```

### Common Mistakes
- Duplicate titles across pages
- Keyword stuffing
- Too long (gets truncated)
- Missing brand name
- Generic titles ("Home", "Services")

## Meta Description

### Best Practices
- **Length**: 150-160 characters (920px display width)
- **Include**: Target keyword naturally
- **CTA**: End with call-to-action
- **Unique**: Different for every page
- **Accurate**: Matches page content

### Templates
```
Service:     Looking for [service] in [city]? [Brand] offers [benefit].
             [Social proof]. Get a free quote today!

Location:    [Brand] provides [service] in [area]. [Years] experience,
             [reviews] reviews. Call [phone] for [offer]!

Blog:        Learn [topic] with our comprehensive guide. Discover [benefit]
             and [benefit]. Updated [date].
```

## Header Tags (H1-H6)

### Hierarchy Rules
```html
<h1>Main Page Title (one per page)</h1>
  <h2>Major Section</h2>
    <h3>Subsection</h3>
      <h4>Detail</h4>
  <h2>Another Major Section</h2>
    <h3>Subsection</h3>
```

### Best Practices
- **One H1 per page** (the main topic)
- **H1 ≠ Title tag** (but should be related)
- **Keyword in H1** (naturally)
- **Logical hierarchy** (don't skip levels)
- **Descriptive** (not just "Services")

## URL Structure

### Best Practices
- **Short**: 3-5 words ideal
- **Descriptive**: Include target keyword
- **Lowercase**: Avoid mixed case
- **Hyphens**: Use hyphens, not underscores
- **No parameters**: Clean URLs preferred

### Examples
```
Good:  /virtual-tours-pittsburgh/
Bad:   /services/virtual-tours?location=pittsburgh&id=123

Good:  /blog/how-to-prepare-for-virtual-tour/
Bad:   /blog/post.php?id=456

Good:  /mount-lebanon-pa-virtual-tours/
Bad:   /location-pages/pennsylvania/allegheny/mount-lebanon/
```

## Image Optimization

### Alt Text Guidelines
```html
<!-- Descriptive, keyword-rich when relevant -->
<img src="office-tour.jpg" alt="360 virtual tour of modern Pittsburgh office space">

<!-- Decorative images -->
<img src="divider.png" alt="">

<!-- Don't keyword stuff -->
<!-- Bad: "virtual tour pittsburgh virtual tours PA virtual tour company" -->
```

### Technical Requirements
- Descriptive filenames (not IMG_001.jpg)
- Compressed (WebP preferred)
- Responsive (srcset)
- Lazy loaded (below fold)
- Width/height attributes (prevent CLS)

## Internal Linking

### Strategy
1. **Hub pages** link to related content
2. **Content clusters** interlink
3. **Breadcrumbs** show hierarchy
4. **Contextual links** in body content
5. **Footer links** for important pages

### Anchor Text Best Practices
```html
<!-- Good: Descriptive -->
<a href="/virtual-tours/">virtual tour services</a>

<!-- Okay: Branded -->
<a href="/about/">about Psybir</a>

<!-- Avoid: Generic -->
<a href="/page/">click here</a>
<a href="/page/">read more</a>
```

## Keyword Placement

### Priority Locations (in order)
1. Title tag
2. H1 heading
3. URL
4. First 100 words
5. H2/H3 headings
6. Image alt text
7. Meta description
8. Body content (naturally)

### Keyword Density
- **No magic number** - write naturally
- **Avoid stuffing** - reads unnaturally
- **Use variations** - synonyms, related terms
- **LSI keywords** - semantically related

## Local On-Page Signals

### NAP Consistency
```
Name:    Psybir Virtual Tours
Address: 123 Main St, Pittsburgh, PA 15213
Phone:   (412) 555-0100

<!-- Same format everywhere -->
```

### Local Keywords
```
[Service] in [City]
[City] [Service] company
Best [Service] near [Neighborhood]
[Service] [City], [State]
```

### Location Pages
Each service area should have:
- Unique title with location
- H1 with location
- Local content (not just swapped city names)
- Local testimonials
- Local images
- NAP information
- Embedded Google Map
- LocalBusiness schema

## E-E-A-T Signals

### Experience
- First-hand knowledge demonstrated
- "I've done this" language
- Photos/videos of actual work
- Dated content showing longevity

### Expertise
- Author credentials
- Industry certifications
- Technical depth
- Comprehensive coverage

### Authority
- Citations from others
- Industry recognition
- Media mentions
- Speaking/teaching

### Trust
- Contact information visible
- Physical address
- Privacy policy
- Secure site (HTTPS)
- Reviews/testimonials

---

_Related: /seo_audit skill, Tier 3 On-Page Optimization_
