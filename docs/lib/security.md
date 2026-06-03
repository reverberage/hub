# Security Guidance — Concrete Snippets

This document contains practical, copy-pasteable guidance for lo6: CSP headers, SSRF validation, Supabase RLS snippets, and LLM-output sanitization patterns.

## Content-Security-Policy (CSP) Example

Add these response headers (Next.js `next.config.js` or middleware) to reduce XSS and data exfiltration risk:

```js
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Content-Security-Policy', value: "default-src 'self'; img-src 'self' data: https:; connect-src 'self' https://api.example.com; script-src 'self'; style-src 'self' 'unsafe-inline'" },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' }
        ]
      }
    ];
  }
};
```

Adjust `connect-src` for allowed API domains. Use `report-uri` or `report-to` in staging to detect violations before enforcing in production.

## SSRF / URL Validation (Node.js example)

Block private IPs and metadata endpoints and enforce an allowlist when possible.

```ts
import { URL } from 'url';

const PRIVATE_IP_RANGES = [
  /^127\./, // loopback
  /^10\./,
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
  /^192\.168\./,
  /^169\.254\./
];

export function isAllowedUrl(raw: string, allowlist: string[] = []) {
  try {
    const u = new URL(raw);
    const hostname = u.hostname;

    // Allow explicit allowlist
    if (allowlist.length && allowlist.includes(hostname)) return true;

    // Prevent metadata services
    if (hostname === '169.254.169.254') return false;

    // Simple private IP check
    for (const re of PRIVATE_IP_RANGES) {
      if (re.test(hostname)) return false;
    }

    // Only http(s) allowed
    if (!['http:', 'https:'].includes(u.protocol)) return false;

    // Optionally perform a DNS lookup and validate the resolved IP is public.
    return true;
  } catch (err) {
    return false;
  }
}
```

Run external fetching from a sandboxed worker with egress controls and request-timeout limits.

## LLM Output Handling Pattern

1. Always treat outputs as untrusted.  
2. Define expected output schema (Zod) and validate.  
3. Sanitize any HTML/Markdown before rendering (DOMPurify server-side).  

Example flow:

```ts
import DOMPurify from 'isomorphic-dompurify';
import { z } from 'zod';

const LLMParagraph = z.object({
  text: z.string(),
  citations: z.array(z.string().url()).optional(),
});

export function sanitizeLLM(raw: unknown) {
  const parsed = LLMParagraph.safeParse(raw);
  if (!parsed.success) throw new Error('LLM output invalid');
  const cleanText = DOMPurify.sanitize(parsed.data.text);
  return { ...parsed.data, text: cleanText };
}
```

Store both raw and sanitized output in an `llm_outputs` audit table with actor_id and timestamp.

## Supabase RLS Example (Row-Level Security)

Assume `stories` table with `owner_id` and roles stored in `auth.users` or a `user_roles` table.

SQL snippet to enforce that only the owner or roles with `editor`/`admin` can update:

```sql
-- Enable RLS
ALTER TABLE public.stories ENABLE ROW LEVEL SECURITY;

-- Policy: owners can update
CREATE POLICY stories_update_owner
  ON public.stories
  FOR UPDATE
  USING (auth.uid() = owner_id);

-- Policy: editors and admins can update
CREATE POLICY stories_update_roles
  ON public.stories
  FOR UPDATE
  USING (
    exists (
      select 1 from public.user_roles ur where ur.user_id = auth.uid() and ur.role in ('editor','admin')
    )
  );
```

Test RLS policies by calling Supabase with a test JWT representing each role and asserting allowed/denied actions.

## CI & Secrets Hygiene (quick checklist)
- Add `.secrets.baseline` and run `detect-secrets` locally and in CI.
- Use GitHub Secrets or a secret manager for production credentials.
- Enforce pre-commit scanning and CI secret scanning (gitleaks/detect-secrets).

## Emergency Kill-switch

Provide an environment-controlled flag that agents check before performing high-impact actions like publishing. Example env var: `AGENTS_ENABLED=false`. Also provide an Admin UI toggle that writes to a signed config row in the DB.
