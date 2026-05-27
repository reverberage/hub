import { describe, expect, it } from 'vitest';
import { canTransitionNewsroomState, newsroomTransitionSchema } from '../../src/lib/validators';

describe('workflow validators', () => {
  it('accepts the Lead to Story transition path used by the LangGraph workflow', () => {
    expect(newsroomTransitionSchema.safeParse({ from: 'LEAD_NEW', to: 'LEAD_TRIAGED' }).success).toBe(true);
    expect(newsroomTransitionSchema.safeParse({ from: 'LEAD_TRIAGED', to: 'LEAD_APPROVED' }).success).toBe(true);
    expect(newsroomTransitionSchema.safeParse({ from: 'LEAD_APPROVED', to: 'STORY_DRAFT' }).success).toBe(true);
    expect(newsroomTransitionSchema.safeParse({ from: 'STORY_DRAFT', to: 'STORY_REVIEW' }).success).toBe(true);
    expect(newsroomTransitionSchema.safeParse({ from: 'STORY_REVIEW', to: 'STORY_APPROVED' }).success).toBe(true);
    expect(newsroomTransitionSchema.safeParse({ from: 'STORY_APPROVED', to: 'STORY_PUBLISHED' }).success).toBe(true);
  });

  it('rejects skipped or cross-pipeline transitions that bypass review gates', () => {
    expect(newsroomTransitionSchema.safeParse({ from: 'LEAD_NEW', to: 'STORY_DRAFT' }).success).toBe(false);
    expect(newsroomTransitionSchema.safeParse({ from: 'STORY_DRAFT', to: 'STORY_PUBLISHED' }).success).toBe(false);
    expect(canTransitionNewsroomState('LEAD_REJECTED', 'STORY_DRAFT')).toBe(false);
  });
});
