# Steam API Terms of Use Summary

**Source:** https://steamcommunity.com/dev/apiterms  
**Last Updated:** July 2010

---

## Key Requirements

### 1. Rate Limit
- **100,000 calls per day** (not per hour as sometimes stated)
- Applies to Steam Web API usage
- Storefront API (store.steampowered.com) has separate limits (~200 requests/5 minutes)

### 2. API Key Requirements
- **Must keep API key confidential** - cannot share with third parties
- Key is personal to you and specific to your Application
- You are personally responsible for use of your API key
- If you become aware of a breach, must notify Valve at webapi@valvesoftware.com

### 3. Privacy Requirements
- Must post a privacy policy regarding use of nonpublic end user data
- Only retrieve Steam Data about users as requested by the end user
- Must inform end users about any Steam Data you will store
- Must store data in countries identified in your privacy policy

### 4. Usage Restrictions
- **No Marketing Use:** Cannot use API for unsolicited marketing communications
- **No Endorsement Claims:** Cannot imply Valve/Steam endorsement
- **No Competitive Advantage:** Cannot create technology for unfair advantage in multiplayer games
- **No Password Interception:** Cannot intercept or store user Steam passwords

### 5. Legal Terms
- **"As Is" Terms:** Valve provides no warranties, disclaims all liability
- **Indemnity:** You agree to hold Valve harmless from third-party claims
- **Jurisdiction:** Washington State, USA
- **Termination:** Valve may terminate API access at any time, for any reason

### 6. Data Distribution
- Can distribute Steam Data to end users for **personal use only**
- Must provide data on "as is" terms with disclaimers
- Must include proper Valve branding/links

### 7. License Terms
- License is personal and specific to your Application
- Cannot transfer or delegate API key to third parties
- Valve may change API at any time without notice
- You are responsible for regularly reviewing API Terms of Use

---

## Implications for Steam Filter Project

### What We Can Do:
- ✅ Use API for personal tool to match game titles
- ✅ Store game metadata (titles, prices, ratings) for user's own use
- ✅ No privacy policy required (not collecting user data, just matching titles)
- ✅ No marketing use (personal tool)

### What We Should Do:
- ⚠️ Keep API key confidential (if we get one)
- ⚠️ Respect rate limits (implement caching to reduce API calls)
- ⚠️ Include proper attribution/links to Steam
- ⚠️ Accept "as is" terms (no warranty on data accuracy)

### Storefront API (Current Approach):
- ✅ No API key required
- ✅ Works for basic game search
- ⚠️ Lower rate limits (~200 requests/5 minutes)
- ⚠️ May be less stable than official Web API
- ✅ Good for personal tools with moderate usage

---

## Recommendations

1. **Continue with Storefront API** for now (no key required, works well)
2. **Implement caching** to minimize API calls (already done in cache.py)
3. **Add attribution** to output (e.g., "Data from Steam")
4. **Consider API key** only if we need advanced features later
5. **Monitor rate limits** - add warnings if approaching limits

---

**Note:** This summary is for reference only. For legal advice, consult the official API Terms of Use document.
