import { describe, expect, it } from 'vitest';
import { createStorySchema, updateStorySchema } from '../../src/lib/validators';

describe('story validators', () => {
  it('accepts valid story inputs', () => {
    expect(createStorySchema.safeParse({
      leadId: '22222222-2222-4222-8222-222222222222',
      title: 'Verified signal from source'
    }).success).toBe(true);

    expect(updateStorySchema.safeParse({
      title: 'Updated story',
      contentMarkdown: '# Draft',
      status: 'REVIEW'
    }).success).toBe(true);
  });

  it('rejects invalid story inputs and unknown fields', () => {
    expect(createStorySchema.safeParse({
      leadId: 'not-a-uuid',
      title: ''
    }).success).toBe(false);

    expect(updateStorySchema.safeParse({
      status: 'LIVE',
      unknown: 'field'
    }).success).toBe(false);
  });
});
