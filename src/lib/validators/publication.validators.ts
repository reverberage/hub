import { z } from 'zod';

export const publicationPlatformSchema = z.enum(['TWITTER', 'BLOG', 'LINKEDIN']);

export const createPublicationSchema = z.object({
  /** UUID of the approved story that should be published. */
  storyId: z.string().uuid(),
  /** External publishing destination for the story. */
  platform: publicationPlatformSchema
}).strict();

export type CreatePublicationInput = z.infer<typeof createPublicationSchema>;
