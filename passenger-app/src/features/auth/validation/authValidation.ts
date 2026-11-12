export const validateIndianMobile = (phone: string): string | undefined => (/^[6-9]\d{9}$/.test(phone) ? undefined : 'Enter a valid 10-digit Indian mobile number.');
export const validateOtp = (otp: string): string | undefined => (/^\d{6}$/.test(otp) ? undefined : 'Enter the six-digit OTP.');
export const validateFullName = (name: string): string | undefined => (name.trim().length >= 2 ? undefined : 'Enter your full name.');
