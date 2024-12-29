import {
  boolean,
  integer,
  json,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";

export const logs = pgTable("logs", {
  id: uuid("id").defaultRandom().primaryKey(),
  action_id: uuid("action_id").references(() => actions.id),
  message: json(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const actions = pgTable("actions", {
  id: uuid("id").defaultRandom().primaryKey(),
  method: text("method"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const sessions = pgTable("sessions", {
  id: uuid("id").primaryKey(),
  browserbaseApiKey: text("browserbase_api_key").notNull(),
  browserbaseProjectId: text("browserbase_project_id").notNull(),
  modelName: text("model_name")
    .$type<
      | "gpt-4o"
      | "gpt-4o-mini"
      | "gpt-4o-2024-08-06"
      | "claude-3-5-sonnet-latest"
      | "claude-3-5-sonnet-20241022"
      | "claude-3-5-sonnet-20240620"
      | "o1-mini"
      | "o1-preview"
    >()
    .notNull(),
  modelApiKey: text("model_api_key").notNull(),
  domSettleTimeoutMs: integer("dom_settle_timeout_ms"),
  verbose: integer("verbose").default(0).$type<0 | 1 | 2>(),
  debugDom: boolean("debug_dom").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

export const schema = {
  logs,
  actions,
  sessions,
};
