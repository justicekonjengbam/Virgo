import { DsLoading } from '../design-system';

type LoadingStateProps = {
  label: string;
};

export function LoadingState({ label }: LoadingStateProps) {
  return <DsLoading label={label} />;
}
