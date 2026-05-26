import { describe, expect, it } from 'vitest';
import { createPublicationSchema } from '../../src/lib/validators';

describe('publication validators', () => {
  it('accepts a valid publication input', () => {
    expect(createPublicationSchema.safeParse({
      storyId: '33333333-3333-4333-8333-333333333333',
      platform: 'BLOG'
    }).success).toBe(true);
  });

  it('rejects invalid publication inputs and unknown fields', () => {
    expect(createPublicationSchema.safeParse({
      storyId: 'not-a-uuid',
      platform: 'MASTODON',
      extra: true
    }).success).toBe(false);
  });
});
