# Dent Sorcery Pipeline: Dan's Methodology Implementation                                                                                         
                                                                                                                                                    
  ## Dan's Entity Model (from ERD)                                                                                                                  
                                                                                                                                                    
  This plan implements Dan's conceptual data model with the full entity relationship structure.                                                     
                                                                                                                                                    
  ```                                                                                                                                               
  ┌─────────────┐    1:many    ┌──────────────┐    targeted by    ┌───────────────┐                                                                 
  │   CLIENT    │─────────────▶│   SERVICE    │◀─────────────────│   LOCATION    │                                                                  
  │ Dent Sorcery│              │ (Product)    │                  │ (Geo-tagged)  │                                                                  
  └─────────────┘              └──────────────┘                  └───────────────┘                                                                  
  │                                  │                                                                                                              
  │                                  │                                                                                                              
  ▼ many:many (RISK)                 ▼                                                                                                              
  ┌──────────────┐                   ┌───────────────┐                                                                                              
  │ COMPETITOR   │◀──────────────────│    SOURCE     │                                                                                              
  │  (Profile)   │   scraped from    │  (Data Type)  │                                                                                              
  └──────────────┘                   └───────────────┘                                                                                              
  │                                                                                                                                                 
  │ analysis produces                                                                                                                               
  ▼                                                                                                                                                 
  ┌──────────────┐                                                                                                                                  
  │   FINDING    │                                                                                                                                  
  │ (Observation)│                                                                                                                                  
  └──────────────┘                                                                                                                                  
  │                                                                                                                                                 
  │ interpreted as                                                                                                                                  
  ▼                                                                                                                                                 
  ┌──────────────┐                                                                                                                                  
  │  ACTIONABLE  │                                                                                                                                  
  │   INSIGHT    │ ◀── THE MISSING BRIDGE                                                                                                           
  └──────────────┘                                                                                                                                  
  │                                                                                                                                                 
  │ generates                                                                                                                                       
  ▼                                                                                                                                                 
  ┌──────────────┐                                                                                                                                  
  │ OUTPUT SPEC  │──▶ Next.js + Content                                                                                                             
  └──────────────┘                                                                                                                                  
  ```                                                                                                                                               
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Canonical Entity Schema (`/schemas/`)                                                                                                          
                                                                                                                                                    
  ### 1. `client.json`                                                                                                                              
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "$schema": "https://json-schema.org/draft/2020-12/schema",                                                                                        
  "title": "Client",                                                                                                                                
  "type": "object",                                                                                                                                 
  "required": ["id", "name", "vertical", "services", "locations"],                                                                                  
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "name": { "type": "string" },                                                                                                                     
  "vertical": { "type": "string", "enum": ["pdr", "plumbing", "hvac", "roofing", "dental", "medspa"] },                                             
  "services": { "type": "array", "items": { "$ref": "service.json" } },                                                                             
  "locations": { "type": "array", "items": { "$ref": "location.json" } },                                                                           
  "constraints": { "$ref": "operational_constraints.json" }                                                                                         
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 2. `service.json`                                                                                                                             
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Service (Product/Solution)",                                                                                                            
  "type": "object",                                                                                                                                 
  "required": ["id", "name", "slug", "is_money_service"],                                                                                           
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "name": { "type": "string" },                                                                                                                     
  "slug": { "type": "string" },                                                                                                                     
  "description": { "type": "string" },                                                                                                              
  "is_money_service": { "type": "boolean" },                                                                                                        
  "keywords": { "type": "array", "items": { "type": "string" } },                                                                                   
  "synonyms": { "type": "array", "items": { "type": "string" } },                                                                                   
  "geo_applicability": { "enum": ["local_radius", "multi_location", "domestic"] },                                                                  
  "defined_variables": {                                                                                                                            
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "time": { "type": "string" },                                                                                                                     
  "cost_range": { "type": "string" },                                                                                                               
  "process_steps": { "type": "array", "items": { "type": "string" } }                                                                               
  }                                                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 3. `location.json`                                                                                                                            
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Location",                                                                                                                              
  "type": "object",                                                                                                                                 
  "required": ["id", "name", "geo_scope", "geo_bucket", "location_cluster"],                                                                        
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "name": { "type": "string" },                                                                                                                     
  "address": { "type": "string" },                                                                                                                  
  "coordinates": {                                                                                                                                  
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "lat": { "type": "number" },                                                                                                                      
  "lng": { "type": "number" }                                                                                                                       
  }                                                                                                                                                 
  },                                                                                                                                                
  "geo_scope": { "enum": ["local_radius", "multi_location", "domestic"] },                                                                          
  "geo_bucket": { "enum": ["0-10", "10-30", "30-60", "60-90", "90+"] },                                                                             
  "location_cluster": { "type": "string" },                                                                                                         
  "is_primary": { "type": "boolean" },                                                                                                              
  "current_rank": { "type": "number" },                                                                                                             
  "target_rank": { "type": "integer" }                                                                                                              
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 4. `source.json` (Dan's Source Data/Targets)                                                                                                  
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Source",                                                                                                                                
  "description": "Data source type - SERP, competitor site, GBP, directory, reviews, socials, etc.",                                                
  "type": "object",                                                                                                                                 
  "required": ["id", "source_type", "url"],                                                                                                         
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "source_type": {                                                                                                                                  
  "enum": [                                                                                                                                         
  "serp_organic",                                                                                                                                   
  "serp_local_pack",                                                                                                                                
  "competitor_website",                                                                                                                             
  "gbp_profile",                                                                                                                                    
  "directory",                                                                                                                                      
  "reviews",                                                                                                                                        
  "social_media",                                                                                                                                   
  "chamber_commerce",                                                                                                                               
  "industry_publication",                                                                                                                           
  "job_board"                                                                                                                                       
  ]                                                                                                                                                 
  },                                                                                                                                                
  "url": { "type": "string", "format": "uri" },                                                                                                     
  "scraped_at": { "type": "string", "format": "date-time" },                                                                                        
  "data_freshness": { "enum": ["current", "recent", "stale"] },                                                                                     
  "geo_tags": { "type": "array", "items": { "$ref": "geo_tag.json" } }                                                                              
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 5. `competitor_profile.json`                                                                                                                  
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Competitor Profile",                                                                                                                    
  "description": "Structured, not vibes - Dan's competitor profile schema",                                                                         
  "type": "object",                                                                                                                                 
  "required": ["id", "domain", "name", "trust_signals", "conversion_mechanics", "seo_structure"],                                                   
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "domain": { "type": "string" },                                                                                                                   
  "name": { "type": "string" },                                                                                                                     
  "sources_scraped": { "type": "array", "items": { "$ref": "source.json" } },                                                                       
  "geo_tags": { "type": "array", "items": { "$ref": "geo_tag.json" } },                                                                             
                                                                                                                                                    
  "trust_signals": {                                                                                                                                
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "review_count": { "type": "integer" },                                                                                                            
  "rating": { "type": "number" },                                                                                                                   
  "review_recency": { "enum": ["recent", "stale", "unknown"] },                                                                                     
  "licenses_shown": { "type": "boolean" },                                                                                                          
  "licenses_location": { "type": "string" },                                                                                                        
  "insurance_shown": { "type": "boolean" },                                                                                                         
  "certs_shown": { "type": "array", "items": { "type": "string" } },                                                                                
  "warranty_guarantee_language": { "type": "string" },                                                                                              
  "real_photos_vs_stock": { "enum": ["real", "stock", "mixed"] },                                                                                   
  "team_photos": { "type": "boolean" },                                                                                                             
  "truck_photos": { "type": "boolean" },                                                                                                            
  "job_photos": { "type": "boolean" },                                                                                                              
  "badges_associations": { "type": "array", "items": { "type": "string" } },                                                                        
  "manufacturer_partnerships": { "type": "array", "items": { "type": "string" } }                                                                   
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "conversion_mechanics": {                                                                                                                         
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "sticky_call": { "type": "boolean" },                                                                                                             
  "form_length": { "type": "integer" },                                                                                                             
  "form_friction_score": { "type": "number", "minimum": 0, "maximum": 1 },                                                                          
  "emergency_language": { "type": "boolean" },                                                                                                      
  "emergency_supported_by_copy": { "type": "boolean" },                                                                                             
  "financing_shown": { "type": "boolean" },                                                                                                         
  "price_anchors": { "type": "boolean" },                                                                                                           
  "what_happens_next_clarity": { "type": "boolean" }                                                                                                
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "seo_structure": {                                                                                                                                
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "page_types_present": {                                                                                                                           
  "type": "array",                                                                                                                                  
  "items": { "enum": ["service", "service-area", "proof-hub", "faq", "blog", "about", "contact"] }                                                  
  },                                                                                                                                                
  "internal_linking_patterns": { "type": "string" },                                                                                                
  "headings_intent_match": { "type": "number", "minimum": 0, "maximum": 1 },                                                                        
  "schema_by_page_type": {                                                                                                                          
  "type": "object",                                                                                                                                 
  "additionalProperties": { "type": "array", "items": { "type": "string" } }                                                                        
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "grid_performance": {                                                                                                                             
  "type": "object",                                                                                                                                 
  "description": "city name -> average rank",                                                                                                       
  "additionalProperties": { "type": "number" }                                                                                                      
  },                                                                                                                                                
                                                                                                                                                    
  "backlinks": {                                                                                                                                    
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "count": { "type": "integer" },                                                                                                                   
  "authority_score": { "type": "integer", "minimum": 0, "maximum": 100 },                                                                           
  "referring_domains": { "type": "integer" }                                                                                                        
  }                                                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 6. `finding.json`                                                                                                                             
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Finding",                                                                                                                               
  "description": "Raw observation from analysis - becomes input to Actionable Insight",                                                             
  "type": "object",                                                                                                                                 
  "required": ["id", "finding_type", "observation", "source_refs"],                                                                                 
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "finding_type": {                                                                                                                                 
  "enum": ["gap", "strength", "opportunity", "threat", "pattern", "anomaly"]                                                                        
  },                                                                                                                                                
  "observation": { "type": "string" },                                                                                                              
  "source_refs": { "type": "array", "items": { "type": "string" } },                                                                                
  "competitor_refs": { "type": "array", "items": { "type": "string" } },                                                                            
  "geo_context": { "$ref": "geo_tag.json" },                                                                                                        
  "confidence": { "type": "number", "minimum": 0, "maximum": 1 },                                                                                   
  "data_points": { "type": "object" }                                                                                                               
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 7. `actionable_insight.json` (THE MISSING BRIDGE)                                                                                             
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Actionable Insight",                                                                                                                    
  "description": "The bridge between findings and output specs - the 'so what'",                                                                    
  "type": "object",                                                                                                                                 
  "required": ["id", "problem", "hypothesis", "evidence", "spec_change", "expected_impact"],                                                        
  "properties": {                                                                                                                                   
  "id": { "type": "string" },                                                                                                                       
  "problem": { "type": "string", "description": "What's missing/weak" },                                                                            
  "hypothesis": { "type": "string", "description": "Why it matters" },                                                                              
  "evidence": {                                                                                                                                     
  "type": "array",                                                                                                                                  
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "source_type": { "type": "string" },                                                                                                              
  "source_id": { "type": "string" },                                                                                                                
  "observation": { "type": "string" }                                                                                                               
  }                                                                                                                                                 
  },                                                                                                                                                
  "description": "Which sources/competitors show the pattern"                                                                                       
  },                                                                                                                                                
  "spec_change": { "type": "string", "description": "What to build/change" },                                                                       
  "expected_impact": {                                                                                                                              
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "rank_impact": { "enum": ["high", "medium", "low"] },                                                                                             
  "cvr_impact": { "enum": ["high", "medium", "low"] },                                                                                              
  "trust_impact": { "enum": ["high", "medium", "low"] },                                                                                            
  "speed_impact": { "enum": ["high", "medium", "low"] }                                                                                             
  }                                                                                                                                                 
  },                                                                                                                                                
  "priority_score": { "type": "number", "minimum": 0, "maximum": 100 },                                                                             
  "geo_context": { "$ref": "geo_tag.json" },                                                                                                        
  "service_context": { "type": "string" }                                                                                                           
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 8. `output_spec.json`                                                                                                                         
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "Output Spec",                                                                                                                           
  "description": "Direct build instructions for Next.js + templates",                                                                               
  "type": "object",                                                                                                                                 
  "required": ["client_id", "page_map", "component_set", "internal_linking_rules", "schema_requirements"],                                          
  "properties": {                                                                                                                                   
  "client_id": { "type": "string" },                                                                                                                
  "generated_at": { "type": "string", "format": "date-time" },                                                                                      
                                                                                                                                                    
  "page_map": {                                                                                                                                     
  "type": "array",                                                                                                                                  
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "route": { "type": "string" },                                                                                                                    
  "page_type": { "enum": ["service", "service-area", "proof-hub", "faq", "home", "contact", "about"] },                                             
  "template": { "type": "string" },                                                                                                                 
  "geo_target": { "$ref": "geo_tag.json" },                                                                                                         
  "service_target": { "type": "string" },                                                                                                           
  "components": { "type": "array", "items": { "type": "string" } },                                                                                 
  "priority": { "type": "integer" }                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "component_set": {                                                                                                                                
  "type": "array",                                                                                                                                  
  "description": "TrustBar, ReviewBlock, ServiceArea module, CTA rules, FAQ rules",                                                                 
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "name": { "type": "string" },                                                                                                                     
  "type": { "enum": ["trust", "conversion", "content", "seo"] },                                                                                    
  "required_data": { "type": "array", "items": { "type": "string" } },                                                                              
  "placement_rules": { "type": "string" }                                                                                                           
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "internal_linking_rules": {                                                                                                                       
  "type": "array",                                                                                                                                  
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "from_page_type": { "type": "string" },                                                                                                           
  "to_page_type": { "type": "string" },                                                                                                             
  "anchor_pattern": { "type": "string" },                                                                                                           
  "placement": { "type": "string" }                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "schema_requirements": {                                                                                                                          
  "type": "array",                                                                                                                                  
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "page_type": { "type": "string" },                                                                                                                
  "schema_types": { "type": "array", "items": { "type": "string" } }                                                                                
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
                                                                                                                                                    
  "llm_answer_blocks": {                                                                                                                            
  "type": "array",                                                                                                                                  
  "description": "LLM SEO - entity-clear, quotable content specs",                                                                                  
  "items": { "$ref": "llm_answer_block.json" }                                                                                                      
  }                                                                                                                                                 
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ### 9. `llm_answer_block.json` (LLM SEO)                                                                                                          
  ```json                                                                                                                                           
  {                                                                                                                                                 
  "title": "LLM Answer Block",                                                                                                                      
  "description": "Unambiguous, quotable, entity-clear content for LLM SEO",                                                                         
  "type": "object",                                                                                                                                 
  "required": ["service", "definition", "triggers", "cost_range", "timeline", "process_steps", "how_to_choose", "faqs"],                            
  "properties": {                                                                                                                                   
  "service": { "type": "string" },                                                                                                                  
  "definition": { "type": "string", "description": "2-sentence 'what it is'" },                                                                     
  "triggers": { "type": "array", "items": { "type": "string" }, "description": "'when you need it'" },                                              
  "cost_range": {                                                                                                                                   
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "range": { "type": "string" },                                                                                                                    
  "variables": { "type": "array", "items": { "type": "string" } },                                                                                  
  "disclaimers": { "type": "string" }                                                                                                               
  }                                                                                                                                                 
  },                                                                                                                                                
  "timeline": { "type": "string" },                                                                                                                 
  "process_steps": { "type": "array", "items": { "type": "string" } },                                                                              
  "how_to_choose": { "type": "array", "items": { "type": "string" }, "description": "checklist" },                                                  
  "faqs": {                                                                                                                                         
  "type": "array",                                                                                                                                  
  "items": {                                                                                                                                        
  "type": "object",                                                                                                                                 
  "properties": {                                                                                                                                   
  "question": { "type": "string" },                                                                                                                 
  "answer": { "type": "string", "description": "tight, direct answer" }                                                                             
  }                                                                                                                                                 
  }                                                                                                                                                 
  },                                                                                                                                                
  "nap_statement": { "type": "string", "description": "consistent NAP/service-area statement" }                                                     
  }                                                                                                                                                 
  }                                                                                                                                                 
  ```                                                                                                                                               
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## 5-Stage Pipeline (Dan's Flow)                                                                                                                  
                                                                                                                                                    
  ```                                                                                                                                               
  ┌─────────────────────────────────────────────────────────────────────────────┐                                                                   
  │ STAGE 1: PLAN                                                                │                                                                  
  │ Generate keyword + geo matrix                                                │                                                                  
  │                                                                              │                                                                  
  │ Input:  Client config (services, locations, constraints)                     │                                                                  
  │ Output: Intent/Geo Matrix artifact                                          │                                                                   
  │ Tools:  DataForSEO keywords, manual seed list                               │                                                                   
  └─────────────────────────────────────────────────────────────────────────────┘                                                                   
  │                                                                                                                                                 
  ▼                                                                                                                                                 
  ┌─────────────────────────────────────────────────────────────────────────────┐                                                                   
  │ STAGE 2: COLLECT                                                             │                                                                  
  │ DataForSEO pulls SERP + Local Finder; Firecrawl pulls pages                 │                                                                   
  │                                                                              │                                                                  
  │ Input:  Intent/Geo Matrix                                                   │                                                                   
  │ Output: Source entities (SERP results, competitor URLs, GBP data)           │                                                                   
  │ Tools:  DataForSEO (organic, local_finder, keywords), Firecrawl (scrape)   │                                                                    
  └─────────────────────────────────────────────────────────────────────────────┘                                                                   
  │                                                                                                                                                 
  ▼                                                                                                                                                 
  ┌─────────────────────────────────────────────────────────────────────────────┐                                                                   
  │ STAGE 3: NORMALIZE                                                           │                                                                  
  │ Map raw scrape → Competitor Profile fields                                   │                                                                  
  │                                                                              │                                                                  
  │ Input:  Raw Source data                                                     │                                                                   
  │ Output: Competitor Profiles (structured, not vibes)                         │                                                                   
  │ Tools:  Firecrawl EXTRACT strategy + normalization logic                    │                                                                   
  └─────────────────────────────────────────────────────────────────────────────┘                                                                   
  │                                                                                                                                                 
  ▼                                                                                                                                                 
  ┌─────────────────────────────────────────────────────────────────────────────┐                                                                   
  │ STAGE 4: SCORE                                                               │                                                                  
  │ Opportunity + gaps + proof deficiency + structure advantage                  │                                                                  
  │                                                                              │                                                                  
  │ Input:  Competitor Profiles + Client context                                │                                                                   
  │ Output: Findings → Actionable Insights (THE BRIDGE)                         │                                                                   
  │ Tools:  Insight rules engine, scoring algorithms                            │                                                                   
  └─────────────────────────────────────────────────────────────────────────────┘                                                                   
  │                                                                                                                                                 
  ▼                                                                                                                                                 
  ┌─────────────────────────────────────────────────────────────────────────────┐                                                                   
  │ STAGE 5: EXPORT                                                              │                                                                  
  │ Output Specs that drive Next.js components + page maps                       │                                                                  
  │                                                                              │                                                                  
  │ Input:  Actionable Insights + Client config                                 │                                                                   
  │ Output: Output Spec (page map, components, linking rules, schema, LLM SEO) │                                                                    
  │ Tools:  Blueprint generator                                                 │                                                                   
  └─────────────────────────────────────────────────────────────────────────────┘                                                                   
  ```                                                                                                                                               
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Intent/Geo Matrix (Artifact produced in Stage 1)                                                                                               
                                                                                                                                                    
  **Rows:** Services (money services)                                                                                                               
  **Cols:** Geo buckets + domestic + multi-location                                                                                                 
  **Cells:** Target page type, keyword cluster, proof requirements, CTA rules, schema requirements                                                  
                                                                                                                                                    
  ### Dent Sorcery Intent/Geo Matrix                                                                                                                
                                                                                                                                                    
  | Service | 0-10 (Bethlehem) | 10-30 (Easton/Northampton) | 30-60 (Quakertown) | Domestic |                                                       
  |---------|------------------|----------------------------|---------------------|----------|                                                      
  | **Paintless Dent Repair** | service-area page, "PDR bethlehem", reviews above fold, sticky call, LocalBusiness+Service | service-area page,     
  "PDR easton", local testimonials, LocalBusiness | service-area page, "PDR quakertown", travel time copy, LocalBusiness | blog/guide, "what        
  is PDR", educational, FAQPage |                                                                                                                   
  | **Door Ding Repair** | service page, "door ding repair bethlehem", before/after gallery, click-to-call | merged with PDR page | merged with     
  PDR page | N/A |                                                                                                                                  
  | **Hail Damage Repair** | service page, "hail damage repair lehigh valley", seasonal content, insurance partnerships, Service schema | same      
  template | same template | blog, "hail season outlook", educational |                                                                             
  | **Crease Removal** | service page, specific damage type | merged | merged | N/A |                                                               
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Files to Create (Implementation)                                                                                                               
                                                                                                                                                    
  ### `/schemas/` directory                                                                                                                         
  ```                                                                                                                                               
  firecrawl_scraper/schemas/                                                                                                                        
  ├── client.json                                                                                                                                   
  ├── service.json                                                                                                                                  
  ├── location.json                                                                                                                                 
  ├── source.json                                                                                                                                   
  ├── competitor_profile.json                                                                                                                       
  ├── finding.json                                                                                                                                  
  ├── actionable_insight.json                                                                                                                       
  ├── output_spec.json                                                                                                                              
  ├── llm_answer_block.json                                                                                                                         
  ├── geo_tag.json                                                                                                                                  
  └── intent_geo_matrix.json                                                                                                                        
  ```                                                                                                                                               
                                                                                                                                                    
  ### `/models/` directory (Pydantic classes from schemas)                                                                                          
  ```                                                                                                                                               
  firecrawl_scraper/models/                                                                                                                         
  ├── entities.py              # Client, Service, Location                                                                                          
  ├── sources.py               # Source entity                                                                                                      
  ├── competitor_profile.py    # Full competitor profile                                                                                            
  ├── findings.py              # Finding entity                                                                                                     
  ├── insights.py              # ActionableInsight entity                                                                                           
  ├── output_specs.py          # OutputSpec, LLMAnswerBlock                                                                                         
  └── geo.py                   # GeoTag, GeoScope, GeoBucket                                                                                        
  ```                                                                                                                                               
                                                                                                                                                    
  ### `/pipeline/` directory (5-stage pipeline)                                                                                                     
  ```                                                                                                                                               
  firecrawl_scraper/pipeline/                                                                                                                       
  ├── __init__.py                                                                                                                                   
  ├── stage_1_plan.py          # Generate Intent/Geo Matrix                                                                                         
  ├── stage_2_collect.py       # DataForSEO + Firecrawl collection                                                                                  
  ├── stage_3_normalize.py     # Raw → Competitor Profiles                                                                                          
  ├── stage_4_score.py         # Findings → Actionable Insights                                                                                     
  ├── stage_5_export.py        # Output Specs generation                                                                                            
  └── orchestrator.py          # Run full pipeline                                                                                                  
  ```                                                                                                                                               
                                                                                                                                                    
  ### `/extraction/` additions                                                                                                                      
  ```                                                                                                                                               
  firecrawl_scraper/extraction/                                                                                                                     
  ├── competitor_extractor.py  # EXTRACT strategy for competitor profiles                                                                           
  ├── geo_tagger.py            # Tag all data with geo keys                                                                                         
  └── source_classifier.py     # Classify source types                                                                                              
  ```                                                                                                                                               
                                                                                                                                                    
  ### `/analysis/` directory                                                                                                                        
  ```                                                                                                                                               
  firecrawl_scraper/analysis/                                                                                                                       
  ├── __init__.py                                                                                                                                   
  ├── insight_rules/           # Rule classes for generating insights                                                                               
  │   ├── backlink_gap.py                                                                                                                           
  │   ├── review_visibility.py                                                                                                                      
  │   ├── certification_check.py                                                                                                                    
  │   ├── gallery_presence.py                                                                                                                       
  │   ├── service_area_coverage.py                                                                                                                  
  │   └── ... (20+ rules)                                                                                                                           
  ├── scoring.py               # Opportunity scoring                                                                                                
  └── matrix_builder.py        # Intent/Geo Matrix generation                                                                                       
  ```                                                                                                                                               
                                                                                                                                                    
  ### `/generators/` directory                                                                                                                      
  ```                                                                                                                                               
  firecrawl_scraper/generators/                                                                                                                     
  ├── __init__.py                                                                                                                                   
  ├── blueprint_generator.py   # OutputSpec generation                                                                                              
  ├── llm_answer_generator.py  # LLM SEO content specs                                                                                              
  └── page_map_generator.py    # Route/page generation                                                                                              
  ```                                                                                                                                               
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Dent Sorcery: Current Data + Gaps                                                                                                              
                                                                                                                                                    
  ### What we have (from existing research)                                                                                                         
  - GBP profile: 200 reviews, 5.0 rating, full business data                                                                                        
  - Grid results: Bethlehem #1, Easton/Northampton #2, Allentown 3.4, Quakertown 16                                                                 
  - Site structure: 19 pages scraped                                                                                                                
  - Competitor list: 5 competitors identified                                                                                                       
  - Backlink data: 2 backlinks (CRITICAL GAP)                                                                                                       
                                                                                                                                                    
  ### What we need to generate                                                                                                                      
  1. **Competitor Profiles** (structured) for all 5 competitors                                                                                     
  2. **Findings** from competitor analysis                                                                                                          
  3. **Actionable Insights** bridging findings to specs                                                                                             
  4. **Intent/Geo Matrix** for all services × geo buckets                                                                                           
  5. **Output Spec** for Next.js build                                                                                                              
  6. **LLM Answer Blocks** for each service                                                                                                         
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Verification Plan                                                                                                                              
                                                                                                                                                    
  1. **Schema validation:** All JSON schemas validate with ajv                                                                                      
  2. **Pipeline test:** Run stages 1-5 with Dent Sorcery data                                                                                       
  3. **Profile extraction:** Verify competitor profiles match schema                                                                                
  4. **Insight quality:** Review generated insights for strategic accuracy                                                                          
  5. **Output spec usability:** Generate Next.js route config from output                                                                           
  6. **End-to-end:** Full pipeline produces valid, buildable output                                                                                 
                                                                                                                                                    
  ---                                                                                                                                               
                                                                                                                                                    
  ## Success Criteria                                                                                                                               
                                                                                                                                                    
  ### Scraper System                                                                                                                                
  - [ ] All 9 JSON schemas defined in `/schemas/`                                                                                                   
  - [ ] All Pydantic models in `/models/`                                                                                                           
  - [ ] 5-stage pipeline implemented in `/pipeline/`                                                                                                
  - [ ] Intent/Geo Matrix generation working                                                                                                        
  - [ ] Competitor profile extraction via Firecrawl EXTRACT                                                                                         
  - [ ] 20+ insight rules implemented                                                                                                               
  - [ ] Output spec generates valid Next.js config                                                                                                  
  - [ ] LLM answer blocks generated per service                                                                                                     
                                                                                                                                                    
  ### Dent Sorcery Deliverables                                                                                                                     
  - [ ] 5 competitor profiles (structured)                                                                                                          
  - [ ] Intent/Geo Matrix artifact                                                                                                                  
  - [ ] 10+ actionable insights with evidence                                                                                                       
  - [ ] Complete output spec (page map + components + schema + LLM blocks)                                                                          
  - [ ] Next.js-ready build instructions                                                                                                            
                                                                                                                                                    
  ### Business Outcomes (3-6 months)                                                                                                                
  - [ ] Backlinks: 2 → 50+                                                                                                                          
  - [ ] Authority: 4/100 → 15+/100                                                                                                                  
  - [ ] Quakertown: rank 16 → top 5                                                                                                                 
  - [ ] Allentown: rank 3.4 → #1