import { describe, expect, it } from 'vitest';
import { createLeadSchema, updateLeadSchema } from '../../src/lib/validators';

describe('lead validators', () => {
  it('accepts valid lead inputs', () => {
    expect(createLeadSchema.safeParse({
      sourceUrl: 'https://example.com/story',
      configId: '11111111-1111-4111-8111-111111111111'
    }).success).toBe(true);

    expect(updateLeadSchema.safeParse({
      status: 'APPROVED',
      relevanceScore: 87
    }).success).toBe(true);
  });

  it('rejects invalid lead inputs and unknown fields', () => {
    expect(createLeadSchema.safeParse({
      sourceUrl: 'not-a-url',
      configId: 'not-a-uuid'
    }).success).toBe(false);

    expect(updateLeadSchema.safeParse({
      status: 'PUBLISHED',
      relevanceScore: 101,
      extra: true
    }).success).toBe(false);
  });
});
