import { isMethodName, methods, type CommandDescriptor, type MethodName, type MethodParams } from '@jam/protocol';
import { useEffect, useState, type FormEvent } from 'react';
import { CommandPalette } from './CommandPalette.tsx';
import { errorMessage } from './errors.ts';
import { fieldsFromSchema, paramsFromForm, type Field } from './schema-fields.ts';

type Outcome = { kind: 'result'; method: MethodName; result: unknown } | { kind: 'error'; message: string };

type PendingForm = { command: CommandDescriptor; fields: Field[] };

export function App() {
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [form, setForm] = useState<PendingForm | null>(null);
  const [outcome, setOutcome] = useState<Outcome | null>(null);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'k' && event.metaKey) {
        event.preventDefault();
        setPaletteOpen((open) => !open);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  async function execute(command: CommandDescriptor, params: Record<string, string>) {
    const { method } = command;
    if (!isMethodName(method)) {
      setOutcome({ kind: 'error', message: `méthode inconnue : ${method}` });
      return;
    }
    try {
      // The core validates params; a wrong value comes back as an error to display.
      const result = await window.jam.call(method, params as MethodParams<typeof method>);
      setOutcome({ kind: 'result', method, result });
    } catch (error) {
      setOutcome({ kind: 'error', message: errorMessage(error) });
    }
  }

  function onSelect(command: CommandDescriptor) {
    try {
      const fields = fieldsFromSchema(command.paramsSchema);
      if (fields.length === 0) {
        void execute(command, {});
      } else {
        setForm({ command, fields });
      }
    } catch (error) {
      setOutcome({ kind: 'error', message: errorMessage(error) });
    }
  }

  return (
    <main>
      <h1>jam</h1>
      <p>
        <kbd>⌘K</kbd> ouvre la palette de commandes.
      </p>
      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} onSelect={onSelect} />
      {form && (
        <CommandForm
          // A new key per command: React starts a fresh form instead of reusing typed values.
          key={form.command.id}
          form={form}
          onCancel={() => setForm(null)}
          onSubmit={(params) => {
            setForm(null);
            void execute(form.command, params);
          }}
        />
      )}
      {outcome && <OutcomeView outcome={outcome} />}
    </main>
  );
}

/** Generic form: one text field per param of the command. */
function CommandForm({
  form,
  onCancel,
  onSubmit,
}: {
  form: PendingForm;
  onCancel: () => void;
  onSubmit: (params: Record<string, string>) => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});

  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit(paramsFromForm(form.fields, values));
  }

  return (
    <form onSubmit={submit}>
      <h2>{form.command.title}</h2>
      {form.fields.map((field, index) => (
        <p key={field.name}>
          <label>
            {field.label}
            <br />
            <input
              name={field.name}
              required={field.required}
              autoFocus={index === 0}
              size={60}
              value={values[field.name] ?? ''}
              onChange={(event) => setValues({ ...values, [field.name]: event.target.value })}
            />
          </label>
        </p>
      ))}
      <button type="submit">Exécuter</button> <button type="button" onClick={onCancel}>Annuler</button>
    </form>
  );
}

/** Shows what the last command returned. Results come from the core and are parsed again here. */
function OutcomeView({ outcome }: { outcome: Outcome }) {
  if (outcome.kind === 'error') {
    return <p role="alert">Erreur : {outcome.message}</p>;
  }
  if (outcome.method === 'repos.list') {
    const repos = methods['repos.list'].result.parse(outcome.result);
    if (repos.length === 0) return <p>Aucun repo.</p>;
    return (
      <ul>
        {repos.map((repo) => (
          <li key={repo.id}>
            <strong>{repo.path}</strong> — tests : <code>{repo.testCommand}</code>
            {repo.acceptanceCommand && (
              <>
                {' '}
                — recette : <code>{repo.acceptanceCommand}</code>
              </>
            )}
          </li>
        ))}
      </ul>
    );
  }
  if (outcome.method === 'repos.add') {
    const repo = methods['repos.add'].result.parse(outcome.result);
    return <p>Repo ajouté : {repo.path}</p>;
  }
  return <pre>{JSON.stringify(outcome.result, null, 2)}</pre>;
}
