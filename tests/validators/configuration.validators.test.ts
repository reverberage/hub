import { describe, expect, it } from 'vitest';
import { createConfigSchema } from '../../src/lib/validators';

describe('configuration validators', () => {
  it('accepts a valid configuration input', () => {
    expect(createConfigSchema.safeParse({
      name: 'Daily AI policy scan',
      sources: [{ type: 'rss', url: 'https://example.com/feed.xml' }],
      interests: ['AI safety', 'newsroom automation'],
      scheduleCron: '0 8 * * *'
    }).success).toBe(true);
  });

  it('rejects invalid source objects and unknown fields', () => {
    expect(createConfigSchema.safeParse({
      name: '',
      sources: [{ type: 'email', url: 'not-a-url' }],
      interests: ['AI'],
      scheduleCron: '0 8 * * *',
      extra: true
    }).success).toBe(false);
  });
});
