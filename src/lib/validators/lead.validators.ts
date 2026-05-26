import { z } from 'zod';

export const leadStatusSchema = z.enum(['NEW', 'TRIAGED', 'REJECTED', 'APPROVED']);

export const createLeadSchema = z.object({
  /** URL of the source item discovered by the sourcing agent. */
  sourceUrl: z.string().url(),
  /** UUID of the configuration that produced this lead. */
  configId: z.string().uuid()
}).strict();

export const updateLeadSchema = z.object({
  /** Current triage state for the lead pipeline. */
  status: leadStatusSchema,
  /** Human or agent relevance score from 0 to 100. */
  relevanceScore: z.number().min(0).max(100)
}).strict();

export type CreateLeadInput = z.infer<typeof createLeadSchema>;
export type UpdateLeadInput = z.infer<typeof updateLeadSchema>;
