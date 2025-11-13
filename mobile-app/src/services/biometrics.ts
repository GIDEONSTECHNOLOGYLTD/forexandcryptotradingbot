/**
 * Biometric Authentication Service
 * Supports Face ID and Touch ID
 */
import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

export class BiometricService {
  private static BIOMETRIC_ENABLED_KEY = 'biometric_enabled';

  /**
   * Check if device supports biometric authentication
   */
  static async isAvailable(): Promise<boolean> {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      return compatible && enrolled;
    } catch (error) {
      console.error('Error checking biometric availability:', error);
      return false;
    }
  }

  /**
   * Get supported biometric types
   */
  static async getSupportedTypes(): Promise<string[]> {
    try {
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      const typeNames: string[] = [];

      types.forEach((type) => {
        switch (type) {
          case LocalAuthentication.AuthenticationType.FINGERPRINT:
            typeNames.push('Touch ID');
            break;
          case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
            typeNames.push('Face ID');
            break;
          case LocalAuthentication.AuthenticationType.IRIS:
            typeNames.push('Iris');
            break;
          default:
            // Unknown biometric type
            break;
        }
      });

      return typeNames;
    } catch (error) {
      console.error('Error getting biometric types:', error);
      return [];
    }
  }

  /**
   * Authenticate user with biometrics
   */
  static async authenticate(
    promptMessage: string = 'Authenticate to continue'
  ): Promise<boolean> {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage,
        fallbackLabel: 'Use Passcode',
        cancelLabel: 'Cancel',
        disableDeviceFallback: false,
      });

      return result.success;
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return false;
    }
  }

  /**
   * Check if biometric login is enabled
   */
  static async isBiometricLoginEnabled(): Promise<boolean> {
    try {
      const enabled = await SecureStore.getItemAsync(this.BIOMETRIC_ENABLED_KEY);
      return enabled === 'true';
    } catch (error) {
      console.error('Error checking biometric login status:', error);
      return false;
    }
  }

  /**
   * Enable biometric login
   */
  static async enableBiometricLogin(): Promise<boolean> {
    try {
      // First authenticate to enable
      const authenticated = await this.authenticate('Enable biometric login');
      
      if (authenticated) {
        await SecureStore.setItemAsync(this.BIOMETRIC_ENABLED_KEY, 'true');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error enabling biometric login:', error);
      return false;
    }
  }

  /**
   * Disable biometric login
   */
  static async disableBiometricLogin(): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(this.BIOMETRIC_ENABLED_KEY);
    } catch (error) {
      console.error('Error disabling biometric login:', error);
    }
  }

  /**
   * Authenticate for login
   */
  static async authenticateForLogin(): Promise<boolean> {
    try {
      const isEnabled = await this.isBiometricLoginEnabled();
      
      if (!isEnabled) {
        return false;
      }

      const types = await this.getSupportedTypes();
      const biometricType = types[0] || 'Biometric';

      return await this.authenticate(`Login with ${biometricType}`);
    } catch (error) {
      console.error('Error authenticating for login:', error);
      return false;
    }
  }

  /**
   * Authenticate for sensitive action
   */
  static async authenticateForAction(action: string): Promise<boolean> {
    try {
      const available = await this.isAvailable();
      
      if (!available) {
        return true; // Skip if not available
      }

      return await this.authenticate(`Authenticate to ${action}`);
    } catch (error) {
      console.error('Error authenticating for action:', error);
      return false;
    }
  }
}
