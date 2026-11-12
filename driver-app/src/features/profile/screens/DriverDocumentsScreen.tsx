import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Linking,
  Pressable,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  View,
} from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverCard } from '../../../components/DriverCard';
import { DriverPageHeader } from '../../../components/DriverPageHeader';
import { DriverText } from '../../../components/DriverText';
import { apiClient } from '../../../services/apiClient';
import { colors, radius, spacing } from '../../../theme';

export interface DriverDocumentItem {
  document_type: string;
  label: string;
  description: string;
  required: boolean;
  is_identity_document: boolean;
  status: 'missing' | 'pending' | 'approved' | 'rejected' | 'expired' | string;
  document_number: string | null;
  original_filename: string | null;
  mime_type: string | null;
  file_size_bytes: number | null;
  uploaded_at: string | null;
  expires_at: string | null;
  expiry_status: 'not_applicable' | 'valid' | 'expiring_soon' | 'expired' | string;
  reviewed_at: string | null;
  rejection_reason: string | null;
}

export interface DriverDocumentsResponse {
  driver_id: number;
  full_name: string;
  phone_number: string;
  total_documents: number;
  verified_count: number;
  pending_count: number;
  missing_count: number;
  rejected_count: number;
  expired_count: number;
  documents: DriverDocumentItem[];
}

export function DriverDocumentsScreen({ onBack }: { onBack: () => void }) {
  const [data, setData] = useState<DriverDocumentsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const response = await apiClient.get<DriverDocumentsResponse>('/api/v1/drivers/me/documents');
      setData(response.data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unable to load documents';
      setError(message);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void fetchDocuments();
  }, [fetchDocuments]);

  const callSupport = () => {
    void Linking.openURL('tel:+916009060341');
  };

  return (
    <SafeAreaView style={styles.safe}>
      <DriverPageHeader onBack={onBack} title="Documents & Compliance" />

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            colors={[colors.primary]}
            onRefresh={() => void fetchDocuments(true)}
            refreshing={isRefreshing}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Verification Policy Banner */}
        <DriverCard style={styles.policyCard}>
          <View style={styles.policyIconContainer}>
            <MaterialCommunityIcons color={colors.primary} name="shield-check" size={28} />
          </View>
          <View style={styles.policyCopy}>
            <DriverText color={colors.primary} size={15} weight="700">
              In-Person Physical Verification
            </DriverText>
            <DriverText color={colors.textSecondary} size={13}>
              All driver documents are verified physically by Virgo operations executives at our
              Imphal office. Drivers cannot edit verified documents.
            </DriverText>
          </View>
        </DriverCard>

        {isLoading && !data ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color={colors.primary} size="large" />
            <DriverText color={colors.textSecondary}>Loading document status…</DriverText>
          </View>
        ) : null}

        {error ? (
          <DriverCard style={styles.errorCard}>
            <MaterialCommunityIcons color={colors.danger} name="alert-circle-outline" size={24} />
            <DriverText color={colors.danger} size={13} style={styles.flexOne}>
              {error}
            </DriverText>
            <Pressable onPress={() => void fetchDocuments()}>
              <DriverText color={colors.primary} size={13} weight="600">
                Retry
              </DriverText>
            </Pressable>
          </DriverCard>
        ) : null}

        {data ? (
          <>
            {/* Quick summary stats */}
            <View style={styles.statsRow}>
              <View style={[styles.statBox, styles.statApproved]}>
                <DriverText color={colors.success} size={20} weight="700">
                  {data.verified_count}
                </DriverText>
                <DriverText color={colors.textSecondary} size={11} weight="500">
                  Approved
                </DriverText>
              </View>
              <View style={[styles.statBox, styles.statPending]}>
                <DriverText color={colors.warning} size={20} weight="700">
                  {data.pending_count}
                </DriverText>
                <DriverText color={colors.textSecondary} size={11} weight="500">
                  Pending
                </DriverText>
              </View>
              <View style={[styles.statBox, styles.statAction]}>
                <DriverText
                  color={data.rejected_count + data.expired_count + data.missing_count > 0 ? colors.danger : colors.textTertiary}
                  size={20}
                  weight="700"
                >
                  {data.rejected_count + data.expired_count + data.missing_count}
                </DriverText>
                <DriverText color={colors.textSecondary} size={11} weight="500">
                  Action Needed
                </DriverText>
              </View>
            </View>

            {/* Document List */}
            <DriverText size={18} weight="700">
              Required Documents
            </DriverText>

            <View style={styles.list}>
              {data.documents.map(doc => (
                <DocumentCard doc={doc} key={doc.document_type} onContactSupport={callSupport} />
              ))}
            </View>

            {/* Support CTA */}
            <DriverCard style={styles.supportCard}>
              <View style={styles.supportIcon}>
                <MaterialCommunityIcons color={colors.primary} name="phone-in-talk" size={24} />
              </View>
              <View style={styles.supportCopy}>
                <DriverText size={15} weight="700">
                  Need to update or submit documents?
                </DriverText>
                <DriverText color={colors.textSecondary} size={13}>
                  Visit our Virgo Operations Hub in Imphal or contact operations support.
                </DriverText>
                <Pressable onPress={callSupport} style={styles.supportButton}>
                  <MaterialCommunityIcons color={colors.white} name="phone" size={16} />
                  <DriverText color={colors.white} size={13} weight="600">
                    Call +91 6009060341
                  </DriverText>
                </Pressable>
              </View>
            </DriverCard>
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function DocumentCard({
  doc,
  onContactSupport,
}: {
  doc: DriverDocumentItem;
  onContactSupport: () => void;
}) {
  const currentStatus = doc.status || (doc as any).verification_status || 'missing';
  const badge = getStatusBadge(currentStatus, doc.expiry_status);

  return (
    <DriverCard style={styles.docCard}>
      <View style={styles.docHeader}>
        <View style={styles.docTitleBlock}>
          <DriverText size={16} weight="700">
            {doc.label}
          </DriverText>
          <DriverText color={colors.textSecondary} size={12}>
            {doc.description}
          </DriverText>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: badge.bgColor }]}>
          <MaterialCommunityIcons color={badge.textColor} name={badge.icon} size={14} />
          <DriverText color={badge.textColor} size={11} weight="600">
            {badge.label}
          </DriverText>
        </View>
      </View>

      {/* Masked Document Number */}
      {doc.document_number ? (
        <View style={styles.detailRow}>
          <DriverText color={colors.textSecondary} size={12}>
            Document No:
          </DriverText>
          <DriverText size={12} weight="600">
            {doc.document_number}
          </DriverText>
        </View>
      ) : null}

      {/* Expiry Date */}
      {doc.expires_at ? (
        <View style={styles.detailRow}>
          <DriverText color={colors.textSecondary} size={12}>
            Expires on:
          </DriverText>
          <DriverText
            color={
              doc.expiry_status === 'expired'
                ? colors.danger
                : doc.expiry_status === 'expiring_soon'
                ? colors.warning
                : colors.textPrimary
            }
            size={12}
            weight="600"
          >
            {formatDate(doc.expires_at)}
          </DriverText>
        </View>
      ) : null}

      {/* Expiring Soon Notice */}
      {doc.expiry_status === 'expiring_soon' ? (
        <View style={styles.expiringNotice}>
          <MaterialCommunityIcons color={colors.warning} name="clock-alert-outline" size={18} />
          <DriverText color={colors.warning} size={12} style={styles.flexOne}>
            This document expires within 30 days. Please renew with Virgo Imphal office to avoid service interruption.
          </DriverText>
        </View>
      ) : null}

      {/* Expired Notice */}
      {doc.expiry_status === 'expired' ? (
        <View style={styles.expiredNotice}>
          <MaterialCommunityIcons color={colors.danger} name="alert-octagon" size={18} />
          <DriverText color={colors.danger} size={12} style={styles.flexOne} weight="600">
            Document has expired. You cannot go online until this document is updated by Virgo Operations.
          </DriverText>
        </View>
      ) : null}

      {/* Rejection Notice */}
      {currentStatus === 'rejected' ? (
        <View style={styles.rejectedNotice}>
          <View style={styles.rejectedHeader}>
            <MaterialCommunityIcons color={colors.danger} name="close-circle-outline" size={18} />
            <DriverText color={colors.danger} size={12} weight="700">
              Needs Correction
            </DriverText>
          </View>
          <DriverText color={colors.danger} size={12}>
            Reason: {doc.rejection_reason || 'Document does not meet Virgo standards.'}
          </DriverText>
          <Pressable onPress={onContactSupport} style={styles.contactLink}>
            <DriverText color={colors.primary} size={12} weight="600">
              Contact Imphal Office for re-verification →
            </DriverText>
          </Pressable>
        </View>
      ) : null}
    </DriverCard>
  );
}

function getStatusBadge(status: string, expiryStatus: string) {
  if (expiryStatus === 'expired') {
    return {
      label: 'Expired',
      icon: 'alert-octagon',
      bgColor: colors.dangerSoft,
      textColor: colors.danger,
    };
  }
  if (expiryStatus === 'expiring_soon') {
    return {
      label: 'Expiring Soon',
      icon: 'clock-alert-outline',
      bgColor: colors.warningSoft,
      textColor: colors.warning,
    };
  }

  switch (status) {
    case 'verified':
    case 'approved':
      return {
        label: 'Approved',
        icon: 'check-circle-outline',
        bgColor: colors.successSoft,
        textColor: colors.success,
      };
    case 'pending':
      return {
        label: 'Under Review',
        icon: 'clock-outline',
        bgColor: colors.warningSoft,
        textColor: colors.warning,
      };
    case 'rejected':
      return {
        label: 'Needs Attention',
        icon: 'alert-circle-outline',
        bgColor: colors.dangerSoft,
        textColor: colors.danger,
      };
    case 'missing':
    default:
      return {
        label: 'Missing',
        icon: 'minus-circle-outline',
        bgColor: colors.surfaceMuted,
        textColor: colors.textTertiary,
      };
  }
}

function formatDate(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return isoString;
  }
}

const styles = StyleSheet.create({
  safe: {
    backgroundColor: colors.background,
    flex: 1,
  },
  content: {
    gap: spacing.lg,
    padding: spacing.xl,
    paddingBottom: spacing.massive,
  },
  flexOne: {
    flex: 1,
  },
  policyCard: {
    backgroundColor: colors.primarySoft,
    borderColor: colors.primaryLight,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.md,
    alignItems: 'flex-start',
    padding: spacing.md,
  },
  policyIconContainer: {
    paddingTop: 2,
  },
  policyCopy: {
    flex: 1,
    gap: spacing.xxs,
  },
  loadingContainer: {
    alignItems: 'center',
    gap: spacing.md,
    paddingVertical: spacing.huge,
  },
  errorCard: {
    alignItems: 'center',
    backgroundColor: colors.dangerSoft,
    flexDirection: 'row',
    gap: spacing.sm,
    padding: spacing.md,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  statBox: {
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    flex: 1,
    gap: 2,
    justifyContent: 'center',
    paddingVertical: spacing.sm,
  },
  statApproved: {
    borderLeftColor: colors.success,
    borderLeftWidth: 4,
  },
  statPending: {
    borderLeftColor: colors.warning,
    borderLeftWidth: 4,
  },
  statAction: {
    borderLeftColor: colors.danger,
    borderLeftWidth: 4,
  },
  list: {
    gap: spacing.md,
  },
  docCard: {
    gap: spacing.sm,
    padding: spacing.md,
  },
  docHeader: {
    alignItems: 'flex-start',
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  docTitleBlock: {
    flex: 1,
    gap: 2,
  },
  statusBadge: {
    alignItems: 'center',
    borderRadius: radius.pill,
    flexDirection: 'row',
    gap: 4,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  detailRow: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  expiringNotice: {
    alignItems: 'center',
    backgroundColor: colors.warningSoft,
    borderRadius: radius.sm,
    flexDirection: 'row',
    gap: spacing.xs,
    padding: spacing.sm,
  },
  expiredNotice: {
    alignItems: 'center',
    backgroundColor: colors.dangerSoft,
    borderRadius: radius.sm,
    flexDirection: 'row',
    gap: spacing.xs,
    padding: spacing.sm,
  },
  rejectedNotice: {
    backgroundColor: colors.dangerSoft,
    borderRadius: radius.sm,
    gap: spacing.xs,
    padding: spacing.sm,
  },
  rejectedHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 4,
  },
  contactLink: {
    marginTop: 2,
  },
  supportCard: {
    alignItems: 'center',
    borderColor: colors.primaryLight,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.md,
    padding: spacing.md,
  },
  supportIcon: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    height: 48,
    justifyContent: 'center',
    width: 48,
  },
  supportCopy: {
    flex: 1,
    gap: spacing.xs,
  },
  supportButton: {
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: colors.primary,
    borderRadius: radius.sm,
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.xs,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
});

