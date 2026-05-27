import { z } from 'zod';

export const leadWorkflowStateSchema = z.enum(['LEAD_NEW', 'LEAD_TRIAGED', 'LEAD_REJECTED', 'LEAD_APPROVED']);
export const storyWorkflowStateSchema = z.enum(['STORY_DRAFT', 'STORY_REVIEW', 'STORY_APPROVED', 'STORY_PUBLISHED']);
export const newsroomWorkflowStateSchema = z.union([leadWorkflowStateSchema, storyWorkflowStateSchema]);

export type NewsroomWorkflowState = z.infer<typeof newsroomWorkflowStateSchema>;

export const newsroomTransitionGraph = {
  LEAD_NEW: ['LEAD_TRIAGED'],
  LEAD_TRIAGED: ['LEAD_REJECTED', 'LEAD_APPROVED'],
  LEAD_REJECTED: [],
  LEAD_APPROVED: ['STORY_DRAFT'],
  STORY_DRAFT: ['STORY_REVIEW'],
  STORY_REVIEW: ['STORY_DRAFT', 'STORY_APPROVED'],
  STORY_APPROVED: ['STORY_PUBLISHED'],
  STORY_PUBLISHED: []
} satisfies Record<NewsroomWorkflowState, readonly NewsroomWorkflowState[]>;

export function canTransitionNewsroomState(from: NewsroomWorkflowState, to: NewsroomWorkflowState): boolean {
  const allowedTargets: readonly NewsroomWorkflowState[] = newsroomTransitionGraph[from];
  return allowedTargets.includes(to);
}

export const newsroomTransitionSchema = z.object({
  from: newsroomWorkflowStateSchema,
  to: newsroomWorkflowStateSchema
}).strict().refine(({ from, to }) => canTransitionNewsroomState(from, to), {
  message: 'Invalid newsroom workflow transition'
});

export type NewsroomTransitionInput = z.infer<typeof newsroomTransitionSchema>;
