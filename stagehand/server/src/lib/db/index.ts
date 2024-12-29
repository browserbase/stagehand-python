import { drizzle } from "drizzle-orm/postgres-js";
import { env } from "../env";
import { schema } from "./schema";

const { DB_HOSTNAME, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME } = env;

const connectionString = `postgres://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOSTNAME}:${DB_PORT}/${DB_NAME}`;

export const db = drizzle({
  connection: connectionString,
  schema,
});
