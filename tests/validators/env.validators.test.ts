import { describe, expect, it } from 'vitest';
import { envSchema } from '../../src/lib/validators';

describe('env validators', () => {
  const validEnv = {
    NEXT_PUBLIC_SUPABASE_URL: 'https://example.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'anon-key',
    SUPABASE_SERVICE_ROLE_KEY: 'service-role-key',
    OPENAI_API_KEY: 'openai-key',
    NEXT_PUBLIC_APP_URL: 'http://localhost:3000'
  };

  it('accepts required startup configuration and optional provider values', () => {
    expect(envSchema.safeParse({
      ...validEnv,
      ANTHROPIC_API_KEY: '',
      GOOGLE_AI_API_KEY: 'google-key',
      REDIS_URL: 'redis://localhost:6379',
      SYSTEM_EXTRA: 'allowed by process.env parsing'
    }).success).toBe(true);
  });

  it('rejects missing secrets and malformed URLs', () => {
    expect(envSchema.safeParse({
      ...validEnv,
      OPENAI_API_KEY: '',
      NEXT_PUBLIC_SUPABASE_URL: 'not-a-url'
    }).success).toBe(false);
  });
});
