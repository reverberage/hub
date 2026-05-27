import { z } from 'zod';

const optionalEnvStringSchema = z.preprocess(
  (value) => value === '' ? undefined : value,
  z.string().min(1).optional()
);

const optionalUrlSchema = z.preprocess(
  (value) => value === '' ? undefined : value,
  z.string().url().optional()
);

export const envSchema = z.object({
  NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  OPENAI_API_KEY: z.string().min(1),
  ANTHROPIC_API_KEY: optionalEnvStringSchema,
  GOOGLE_AI_API_KEY: optionalEnvStringSchema,
  REDIS_URL: optionalUrlSchema,
  NEXT_PUBLIC_APP_URL: z.string().url()
});

export type EnvInput = z.infer<typeof envSchema>;
