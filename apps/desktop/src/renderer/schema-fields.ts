import { z } from 'zod';

// The palette builds a form from a command's params JSON Schema, so a new
// command needs no UI code. S1 scope: flat objects whose properties are strings.

export type Field = { name: string; label: string; required: boolean };

const objectSchema = z.object({
  properties: z
    .record(z.string(), z.object({ type: z.string().optional(), description: z.string().optional() }))
    .default({}),
  required: z.array(z.string()).default([]),
});

export function fieldsFromSchema(schema: unknown): Field[] {
  const { properties, required } = objectSchema.parse(schema);
  return Object.entries(properties).map(([name, property]) => {
    if (property.type !== 'string') {
      // Better to fail loudly than to show a form that silently misses a param.
      throw new Error(`param "${name}" has type ${property.type ?? 'unknown'}; the palette only handles strings`);
    }
    return { name, label: property.description ?? name, required: required.includes(name) };
  });
}

/**
 * Turns form inputs into call params. An empty optional field means "not given".
 * An empty required field is kept so that the core, which owns validation,
 * answers with a clear error.
 */
export function paramsFromForm(fields: Field[], values: Record<string, string>): Record<string, string> {
  const params: Record<string, string> = {};
  for (const field of fields) {
    const value = values[field.name] ?? '';
    if (field.required || value.trim() !== '') params[field.name] = value;
  }
  return params;
}
