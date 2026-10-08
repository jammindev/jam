import type { CommandDescriptor } from '@jam/protocol';
import { Command } from 'cmdk';
import { useEffect, useState } from 'react';
import { errorMessage } from './errors.ts';

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelect: (command: CommandDescriptor) => void;
};

/**
 * Cmd+K palette. It lists the core's command registry (ADR 0007), so a command
 * added to the core shows up here without UI changes. cmdk handles filtering,
 * keyboard navigation and accessibility.
 */
export function CommandPalette({ open, onOpenChange, onSelect }: Props) {
  const [commands, setCommands] = useState<CommandDescriptor[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Reload on every opening: the registry lives in the core, not in the UI.
  useEffect(() => {
    if (!open) return;
    window.jam
      .call('commands.list', {})
      .then((list) => {
        setCommands(list);
        setLoadError(null);
      })
      .catch((error: unknown) => setLoadError(errorMessage(error)));
  }, [open]);

  return (
    <Command.Dialog open={open} onOpenChange={onOpenChange} label="Palette de commandes">
      <Command.Input placeholder="Rechercher une commande…" autoFocus />
      <Command.List>
        <Command.Empty>{loadError ? `Erreur : ${loadError}` : 'Aucune commande'}</Command.Empty>
        {commands.map((command) => (
          <Command.Item
            key={command.id}
            value={command.title}
            onSelect={() => {
              onOpenChange(false);
              onSelect(command);
            }}
          >
            {command.title}
          </Command.Item>
        ))}
      </Command.List>
    </Command.Dialog>
  );
}
