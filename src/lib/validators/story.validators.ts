import { z } from 'zod';

export const storyStatusSchema = z.enum(['DRAFT', 'REVIEW', 'APPROVED', 'PUBLISHED']);

export const createStorySchema = z.object({
  /** UUID of the approved lead this story was created from. */
  leadId: z.string().uuid(),
  /** Human-readable story headline shown in the editorial workflow. */
  title: z.string().min(1).max(500)
}).strict();

export const updateStorySchema = z.object({
  /** Updated story headline, when the title changes. */
  title: z.string().min(1).max(500).optional(),
  /** Draft body in Markdown produced or edited by the newsroom workflow. */
  contentMarkdown: z.string().optional(),
  /** Editorial lifecycle state for the story. */
  status: storyStatusSchema.optional()
}).strict();

export type CreateStoryInput = z.infer<typeof createStorySchema>;
export type UpdateStoryInput = z.infer<typeof updateStorySchema>;
