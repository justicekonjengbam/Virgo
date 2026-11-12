import { apiClient } from '../../../services/apiClient';

export type EmergencyContact = {
  id: number;
  name: string;
  phone_number: string;
  relationship: string | null;
};

export const emergencyContactsApi = {
  list: async () =>
    (await apiClient.get<EmergencyContact[]>('/api/v1/passengers/me/emergency-contacts')).data,
};
