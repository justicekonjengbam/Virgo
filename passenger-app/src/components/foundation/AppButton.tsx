import { DsButton } from '../design-system';

type AppButtonProps = {
  title: string;
  onPress: () => void;
  disabled?: boolean;
};

export function AppButton({ title, onPress, disabled = false }: AppButtonProps) {
  return <DsButton disabled={disabled} label={title} onPress={onPress} />;
}
