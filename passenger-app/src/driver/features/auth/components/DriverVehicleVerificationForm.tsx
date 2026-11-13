import { useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { errorCodes, isErrorWithCode, pick, types } from '@react-native-documents/picker';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DriverButton } from '../../../components/DriverButton';
import { DriverCard } from '../../../components/DriverCard';
import { DriverText } from '../../../components/DriverText';
import { DriverTextField } from '../../../components/DriverTextField';
import { colors, spacing } from '../../../theme';
import {
  driverAuthService,
  type DriverRegistrationIdentity,
  type DriverSession,
} from '../services/driverAuthService';
import { driverAuthError } from '../utils/driverAuthError';

type Props = {
  identity: DriverRegistrationIdentity;
  onCompleted: (session: DriverSession) => void;
};
type DocumentType = 'driving_licence' | 'vehicle_registration' | 'aadhaar' | 'vehicle_insurance';
const documents: [DocumentType, string, string][] = [
  ['driving_licence', 'Driving Licence', 'Driving licence number'],
  ['vehicle_registration', 'Vehicle Registration (RC)', 'Vehicle registration number'],
  ['aadhaar', 'Aadhaar Card', 'Aadhaar card number'],
  ['vehicle_insurance', 'Vehicle Insurance', 'Insurance policy number'],
];
const seatsByVehicleType = { car: '4', bike: '2', auto: '3' } as const;

export function DriverVehicleVerificationForm({ identity, onCompleted }: Props) {
  const [city, setCity] = useState('Hubali');
  const [registration, setRegistration] = useState('');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [color, setColor] = useState('');
  const [category, setCategory] = useState<'car' | 'bike' | 'auto'>('car');
  const [seats, setSeats] = useState('4');
  const [numbers, setNumbers] = useState<Record<DocumentType, string>>({
    driving_licence: '',
    vehicle_registration: '',
    aadhaar: '',
    vehicle_insurance: '',
  });
  const [files, setFiles] = useState<Partial<Record<DocumentType, string>>>({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const choose = async (type: DocumentType) => {
    try {
      const [file] = await pick({ allowMultiSelection: false, type: [types.images, types.pdf] });
      setFiles((current) => ({ ...current, [type]: file.uri }));
      setMessage('');
    } catch (error) {
      if (!isErrorWithCode(error) || error.code !== errorCodes.OPERATION_CANCELED) setMessage('Unable to select this document. Please try again.');
    }
  };
  const submit = async () => {
    if (
      !city.trim() ||
      !registration.trim() ||
      !make.trim() ||
      !model.trim() ||
      !/^\d{4}$/.test(year) ||
      !/^\d+$/.test(seats) ||
      documents.some(([type]) => numbers[type].trim().length < 4 || !files[type])
    ) {
      setMessage('Add every required document number, file, and vehicle field.');
      return;
    }
    setLoading(true);
    setMessage('');
    try {
      const session = await driverAuthService.completeRegistration(identity, {
        operating_city: city.trim(),
        registration_number: registration.trim().toUpperCase(),
        vehicle_make: make.trim(),
        vehicle_model: model.trim(),
        vehicle_year: Number(year),
        vehicle_color: color.trim() || undefined,
        vehicle_category: category,
        seat_count: Number(seats),
        documents: documents.map(([type]) => ({
          document_type: type,
          document_number: numbers[type].trim(),
          storage_key: files[type]!,
        })),
      });
      onCompleted(session);
    } catch (error) {
      setMessage(driverAuthError(error));
    } finally {
      setLoading(false);
    }
  };
  return (
    <View style={styles.form}>
      <DriverText size={20} weight="700">
        Verify your details
      </DriverText>
      <DriverText color={colors.textSecondary}>
        Add every document and vehicle detail. Virgo saves this application only when you submit.
      </DriverText>
      {documents.map(([type, title, label]) => (
        <View key={type} style={styles.document}>
          <DriverTextField
            label={label}
            onChangeText={(value) => setNumbers((current) => ({ ...current, [type]: value }))}
            placeholder={`Enter ${title.toLowerCase()} number`}
            value={numbers[type]}
          />
          <Pressable
            accessibilityRole="button"
            onPress={() => void choose(type)}
            style={styles.upload}
          >
            <MaterialCommunityIcons
              color={colors.primary}
              name={files[type] ? 'check-circle' : 'cloud-upload-outline'}
              size={25}
            />
            <DriverText color={colors.primary} weight="600">
              {files[type] ? 'Document selected' : `Upload ${title}`}
            </DriverText>
          </Pressable>
        </View>
      ))}
      <DriverTextField
        autoCapitalize="characters"
        label="Vehicle registration number"
        onChangeText={setRegistration}
        placeholder="KA25AB1234"
        value={registration}
      />
      <DriverTextField
        label="City of operation"
        onChangeText={setCity}
        placeholder="Hubali"
        value={city}
      />
      <DriverTextField
        label="Vehicle make"
        onChangeText={setMake}
        placeholder="Maruti Suzuki"
        value={make}
      />
      <DriverTextField
        label="Vehicle model"
        onChangeText={setModel}
        placeholder="Swift Desire"
        value={model}
      />
      <DriverTextField
        inputMode="numeric"
        label="Vehicle year"
        maxLength={4}
        onChangeText={setYear}
        placeholder="2022"
        value={year}
      />
      <DriverTextField
        label="Vehicle colour (optional)"
        onChangeText={setColor}
        placeholder="White"
        value={color}
      />
      <DriverText weight="600">Vehicle type</DriverText>
      <View style={styles.categories}>
        {(['car', 'bike', 'auto'] as const).map((item) => (
          <DriverButton
            key={item}
            label={item[0].toUpperCase() + item.slice(1)}
            onPress={() => {
              setCategory(item);
              setSeats(seatsByVehicleType[item]);
            }}
            size="medium"
            variant={category === item ? 'primary' : 'secondary'}
          />
        ))}
      </View>
      <DriverTextField
        inputMode="numeric"
        label="Number of seats"
        maxLength={2}
        onChangeText={setSeats}
        placeholder="Enter seat count"
        value={seats}
      />
      <DriverCard style={styles.notice}>
        <MaterialCommunityIcons color={colors.primary} name="shield-check-outline" size={28} />
        <DriverText style={styles.noticeText}>
          Your profile, vehicle, and documents are submitted together for verification.
        </DriverText>
      </DriverCard>
      {message ? <DriverText color={colors.error}>{message}</DriverText> : null}
      <DriverButton
        label="Submit Driver Application"
        loading={loading}
        onPress={() => void submit()}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  form: { gap: spacing.lg },
  document: { gap: spacing.sm },
  upload: {
    alignItems: 'center',
    borderColor: colors.primary,
    borderRadius: 12,
    borderWidth: 1,
    flexDirection: 'row',
    gap: spacing.sm,
    justifyContent: 'center',
    minHeight: 52,
  },
  categories: { flexDirection: 'row', gap: spacing.sm },
  notice: {
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    flexDirection: 'row',
    gap: spacing.md,
    padding: spacing.lg,
  },
  noticeText: { flex: 1 },
});
