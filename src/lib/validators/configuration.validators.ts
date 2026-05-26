import { z } from 'zod';

export const sourceTypeSchema = z.enum(['rss', 'twitter', 'crawler', 'network_signal']);

export const sourceObjectSchema = z.object({
  /** Type of source adapter the sourcing agent should use. */
  type: sourceTypeSchema,
  /** URL for the RSS feed, social source, crawler seed, or network signal. */
  url: z.string().url()
}).strict();

export const createConfigSchema = z.object({
  /** Display name for this newsroom sourcing configuration. */
  name: z.string().min(1),
  /** Source definitions used by the sourcing agent. */
  sources: z.array(sourceObjectSchema),
  /** Topics, beats, or keywords used to score incoming leads. */
  interests: z.array(z.string()),
  /** Cron expression controlling the sourcing schedule. */
  scheduleCron: z.string()
}).strict();

export type SourceObjectInput = z.infer<typeof sourceObjectSchema>;
export type CreateConfigInput = z.infer<typeof createConfigSchema>;
