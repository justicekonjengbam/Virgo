import { useCallback, useEffect, useState } from 'react';
import { SafeAreaView, StyleSheet, View } from 'react-native';

import { AppButton } from '../../../components/foundation/AppButton';
import { AppText } from '../../../components/foundation/AppText';
import { LoadingState } from '../../../components/feedback/LoadingState';
import { ApiError } from '../../../services/apiClient';
import { colors, radius, spacing } from '../../../theme/tokens';
import { healthService, type HealthStatus } from '../services/healthService';

type ConnectionState = 'loading' | 'connected' | 'failed';

const getErrorMessage = (error: unknown): string =>
  error instanceof ApiError ? error.message : 'Connection Failed';

export function HealthCheckScreen() {
  const [connectionState, setConnectionState] = useState<ConnectionState>('loading');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  const checkHealth = useCallback(async () => {
    setConnectionState('loading');
    setErrorMessage('');

    try {
      const response = await healthService.check();
      setHealth(response);
      setConnectionState('connected');
    } catch (error) {
      setHealth(null);
      setErrorMessage(getErrorMessage(error));
      setConnectionState('failed');
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    void healthService
      .check()
      .then((response) => {
        if (!isMounted) {
          return;
        }

        setHealth(response);
        setConnectionState('connected');
      })
      .catch((error) => {
        if (!isMounted) {
          return;
        }

        setErrorMessage(getErrorMessage(error));
        setConnectionState('failed');
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.content}>
        <AppText variant="title">Backend Health Check</AppText>

        {connectionState === 'loading' && <LoadingState label="Checking backend..." />}

        {connectionState === 'connected' && health && (
          <View accessibilityLiveRegion="polite" style={styles.card}>
            <AppText style={styles.success}>Backend Connected</AppText>
            <AppText variant="caption">Version {health.version}</AppText>
            <AppText variant="caption">Environment: {health.environment}</AppText>
          </View>
        )}

        {connectionState === 'failed' && (
          <View accessibilityLiveRegion="polite" style={styles.card}>
            <AppText style={styles.error}>Connection Failed</AppText>
            <AppText variant="caption">{errorMessage}</AppText>
          </View>
        )}

        {connectionState !== 'loading' && <AppButton onPress={checkHealth} title="Retry" />}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: colors.background,
    flex: 1,
  },
  content: {
    flex: 1,
    gap: spacing.lg,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.sm,
    padding: spacing.lg,
  },
  success: {
    color: colors.success,
    fontSize: 18,
    fontWeight: '700',
  },
  error: {
    color: colors.error,
    fontSize: 18,
    fontWeight: '700',
  },
});
