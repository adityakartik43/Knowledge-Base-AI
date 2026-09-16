import 'dotenv/config';
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  schema: 'prisma/schema.prisma',

  migrations: {
    path: 'prisma/migrations',
  },

  datasource: {
    // Supabase pooled URL (pgbouncer) is not suitable for migrations/DDL.
    url: env('DIRECT_URL'),
  },
});
