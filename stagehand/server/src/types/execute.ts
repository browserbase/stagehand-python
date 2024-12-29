import { z } from "zod";

export const executeRequestSchema = z.object({
  method: z.union([
    z.literal("act"),
    z.literal("extract"),
    z.literal("observe"),
    z.string(),
  ]),
  args: z.array(z.unknown()),
});
