# Technical SEO Reference

## Core Web Vitals Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5s - 4s | >4s |
| **FID** (First Input Delay) | ≤100ms | 100ms - 300ms | >300ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1 - 0.25 | >0.25 |
| **INP** (Interaction to Next Paint) | ≤200ms | 200ms - 500ms | >500ms |
| **TTFB** (Time to First Byte) | ≤800ms | 800ms - 1.8s | >1.8s |

## Crawlability Checklist

### Robots.txt
```
# Good robots.txt example
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/
Disallow: /cart/
Disallow: /checkout/

Sitemap: https://example.com/sitemap.xml
```

**Common Mistakes:**
- Blocking CSS/JS files (prevents rendering)
- Blocking images (prevents image search)
- Blocking entire site during development
- Missing sitemap reference

### XML Sitemap Requirements
- Valid XML format
- ≤50,000 URLs per sitemap
- ≤50MB uncompressed
- Updated lastmod dates
- Only indexable URLs (no redirects, no 404s)
- Submitted to GSC

### Canonical Tags
```html
<!-- Self-referencing canonical (recommended) -->
<link rel="canonical" href="https://example.com/page/" />

<!-- Cross-domain canonical -->
<link rel="canonical" href="https://primary-domain.com/page/" />
```

**Best Practices:**
- Every page should have a canonical
- Use absolute URLs
- Self-reference if unique content
- Point to preferred URL version

## HTTP Status Codes

| Code | Meaning | SEO Impact | Action |
|------|---------|------------|--------|
| 200 | OK | Good | None |
| 301 | Permanent Redirect | Passes ~90% link equity | Use for permanent moves |
| 302 | Temporary Redirect | Less link equity passed | Use only for temporary |
| 404 | Not Found | Negative if many | Fix or redirect |
| 410 | Gone | Faster deindex | Use for intentional removal |
| 500 | Server Error | Very negative | Fix immediately |
| 503 | Service Unavailable | Temporary issue | Use during maintenance |

## Mobile-First Indexing

### Required Elements
- [ ] Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] Same content on mobile as desktop
- [ ] Same structured data on both versions
- [ ] Same meta tags on both versions
- [ ] Responsive images with srcset
- [ ] Touch-friendly tap targets (≥48px)

### Mobile Testing
```bash
# Test with Google's Mobile-Friendly Test
# Check: Page loading issues, Viewport issues, Content sizing, Clickable elements
```

## HTTPS Implementation

### Requirements
- Valid SSL certificate
- All resources loaded over HTTPS (no mixed content)
- HTTP redirects to HTTPS (301)
- HSTS header recommended
- Update internal links to HTTPS
- Update canonical tags to HTTPS
- Update sitemap URLs to HTTPS

### Common Issues
- Mixed content (HTTP resources on HTTPS page)
- Redirect chains (HTTP → HTTPS → www)
- Certificate expiration
- Wrong certificate domain

## JavaScript SEO

### Rendering Considerations
- Google uses Chrome 41 for initial crawl
- Dynamic content may not be indexed immediately
- Use server-side rendering (SSR) for critical content
- Implement dynamic rendering for JS-heavy sites
- Test with "URL Inspection" in GSC

### Best Practices
- Critical content in initial HTML
- Avoid JavaScript-only navigation
- Use progressive enhancement
- Test with JavaScript disabled
- Monitor Coverage report in GSC

## Structured Data Validation

### Testing Tools
1. Google Rich Results Test
2. Schema.org Validator
3. JSON-LD Playground

### Common Schema Types for Local Business
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Business Name",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "Pittsburgh",
    "addressRegion": "PA",
    "postalCode": "15213"
  },
  "telephone": "+1-412-555-0100",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "40.4406",
    "longitude": "-79.9959"
  },
  "openingHoursSpecification": [...],
  "aggregateRating": {...}
}
```

## Page Speed Optimization

### Quick Wins
1. **Compress images** - Use WebP, proper sizing
2. **Enable compression** - Gzip/Brotli
3. **Minify CSS/JS** - Remove whitespace
4. **Browser caching** - Set cache headers
5. **Remove render-blocking resources** - Defer non-critical JS

### Advanced
- Critical CSS inlining
- Lazy loading images/videos
- Preload key resources
- CDN for static assets
- Database query optimization

---

_Related: /seo_audit skill, Tier 2 Technical Foundations_
