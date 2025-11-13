/**
 * Internationalization (i18n) Support
 * Multi-language support for the app
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Localization from 'expo-localization';

export type SupportedLanguage = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja' | 'ar';

const LANGUAGE_STORAGE_KEY = 'app_language';

// Translation strings
const translations: Record<SupportedLanguage, Record<string, string>> = {
  en: {
    // Auth
    'auth.login': 'Login',
    'auth.signup': 'Sign Up',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.forgotPassword': 'Forgot Password?',
    'auth.dontHaveAccount': "Don't have an account?",
    'auth.alreadyHaveAccount': 'Already have an account?',
    
    // Navigation
    'nav.home': 'Home',
    'nav.trading': 'Trading',
    'nav.portfolio': 'Portfolio',
    'nav.settings': 'Settings',
    
    // Bot
    'bot.create': 'Create Bot',
    'bot.start': 'Start',
    'bot.stop': 'Stop',
    'bot.delete': 'Delete',
    'bot.edit': 'Edit',
    'bot.performance': 'Performance',
    'bot.status': 'Status',
    
    // Common
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.retry': 'Retry',
  },
  
  es: {
    // Spanish
    'auth.login': 'Iniciar sesión',
    'auth.signup': 'Registrarse',
    'auth.email': 'Correo electrónico',
    'auth.password': 'Contraseña',
    'auth.forgotPassword': '¿Olvidaste tu contraseña?',
    'auth.dontHaveAccount': '¿No tienes una cuenta?',
    'auth.alreadyHaveAccount': '¿Ya tienes una cuenta?',
    
    'nav.home': 'Inicio',
    'nav.trading': 'Trading',
    'nav.portfolio': 'Cartera',
    'nav.settings': 'Configuración',
    
    'bot.create': 'Crear Bot',
    'bot.start': 'Iniciar',
    'bot.stop': 'Detener',
    'bot.delete': 'Eliminar',
    'bot.edit': 'Editar',
    'bot.performance': 'Rendimiento',
    'bot.status': 'Estado',
    
    'common.save': 'Guardar',
    'common.cancel': 'Cancelar',
    'common.confirm': 'Confirmar',
    'common.loading': 'Cargando...',
    'common.error': 'Error',
    'common.success': 'Éxito',
    'common.retry': 'Reintentar',
  },
  
  fr: {
    // French
    'auth.login': 'Connexion',
    'auth.signup': "S'inscrire",
    'auth.email': 'Email',
    'auth.password': 'Mot de passe',
    'auth.forgotPassword': 'Mot de passe oublié?',
    'auth.dontHaveAccount': "Vous n'avez pas de compte?",
    'auth.alreadyHaveAccount': 'Vous avez déjà un compte?',
    
    'nav.home': 'Accueil',
    'nav.trading': 'Trading',
    'nav.portfolio': 'Portefeuille',
    'nav.settings': 'Paramètres',
    
    'bot.create': 'Créer un Bot',
    'bot.start': 'Démarrer',
    'bot.stop': 'Arrêter',
    'bot.delete': 'Supprimer',
    'bot.edit': 'Modifier',
    'bot.performance': 'Performance',
    'bot.status': 'Statut',
    
    'common.save': 'Enregistrer',
    'common.cancel': 'Annuler',
    'common.confirm': 'Confirmer',
    'common.loading': 'Chargement...',
    'common.error': 'Erreur',
    'common.success': 'Succès',
    'common.retry': 'Réessayer',
  },
  
  de: {
    // German
    'auth.login': 'Anmelden',
    'auth.signup': 'Registrieren',
    'auth.email': 'E-Mail',
    'auth.password': 'Passwort',
    'auth.forgotPassword': 'Passwort vergessen?',
    'auth.dontHaveAccount': 'Kein Konto?',
    'auth.alreadyHaveAccount': 'Bereits ein Konto?',
    
    'nav.home': 'Startseite',
    'nav.trading': 'Handel',
    'nav.portfolio': 'Portfolio',
    'nav.settings': 'Einstellungen',
    
    'bot.create': 'Bot erstellen',
    'bot.start': 'Starten',
    'bot.stop': 'Stoppen',
    'bot.delete': 'Löschen',
    'bot.edit': 'Bearbeiten',
    'bot.performance': 'Leistung',
    'bot.status': 'Status',
    
    'common.save': 'Speichern',
    'common.cancel': 'Abbrechen',
    'common.confirm': 'Bestätigen',
    'common.loading': 'Laden...',
    'common.error': 'Fehler',
    'common.success': 'Erfolg',
    'common.retry': 'Wiederholen',
  },
  
  zh: {
    // Chinese
    'auth.login': '登录',
    'auth.signup': '注册',
    'auth.email': '电子邮件',
    'auth.password': '密码',
    'auth.forgotPassword': '忘记密码？',
    'auth.dontHaveAccount': '没有账户？',
    'auth.alreadyHaveAccount': '已有账户？',
    
    'nav.home': '首页',
    'nav.trading': '交易',
    'nav.portfolio': '投资组合',
    'nav.settings': '设置',
    
    'bot.create': '创建机器人',
    'bot.start': '开始',
    'bot.stop': '停止',
    'bot.delete': '删除',
    'bot.edit': '编辑',
    'bot.performance': '表现',
    'bot.status': '状态',
    
    'common.save': '保存',
    'common.cancel': '取消',
    'common.confirm': '确认',
    'common.loading': '加载中...',
    'common.error': '错误',
    'common.success': '成功',
    'common.retry': '重试',
  },
  
  ja: {
    // Japanese
    'auth.login': 'ログイン',
    'auth.signup': '登録',
    'auth.email': 'メール',
    'auth.password': 'パスワード',
    'auth.forgotPassword': 'パスワードをお忘れですか？',
    'auth.dontHaveAccount': 'アカウントをお持ちでないですか？',
    'auth.alreadyHaveAccount': 'すでにアカウントをお持ちですか？',
    
    'nav.home': 'ホーム',
    'nav.trading': '取引',
    'nav.portfolio': 'ポートフォリオ',
    'nav.settings': '設定',
    
    'bot.create': 'ボットを作成',
    'bot.start': '開始',
    'bot.stop': '停止',
    'bot.delete': '削除',
    'bot.edit': '編集',
    'bot.performance': 'パフォーマンス',
    'bot.status': 'ステータス',
    
    'common.save': '保存',
    'common.cancel': 'キャンセル',
    'common.confirm': '確認',
    'common.loading': '読み込み中...',
    'common.error': 'エラー',
    'common.success': '成功',
    'common.retry': '再試行',
  },
  
  ar: {
    // Arabic
    'auth.login': 'تسجيل الدخول',
    'auth.signup': 'التسجيل',
    'auth.email': 'البريد الإلكتروني',
    'auth.password': 'كلمة المرور',
    'auth.forgotPassword': 'نسيت كلمة المرور؟',
    'auth.dontHaveAccount': 'ليس لديك حساب؟',
    'auth.alreadyHaveAccount': 'هل لديك حساب بالفعل؟',
    
    'nav.home': 'الرئيسية',
    'nav.trading': 'التداول',
    'nav.portfolio': 'المحفظة',
    'nav.settings': 'الإعدادات',
    
    'bot.create': 'إنشاء بوت',
    'bot.start': 'بدء',
    'bot.stop': 'إيقاف',
    'bot.delete': 'حذف',
    'bot.edit': 'تعديل',
    'bot.performance': 'الأداء',
    'bot.status': 'الحالة',
    
    'common.save': 'حفظ',
    'common.cancel': 'إلغاء',
    'common.confirm': 'تأكيد',
    'common.loading': 'جاري التحميل...',
    'common.error': 'خطأ',
    'common.success': 'نجاح',
    'common.retry': 'إعادة المحاولة',
  },
};

class I18n {
  private currentLanguage: SupportedLanguage = 'en';

  async init() {
    // Try to load saved language
    const savedLanguage = await AsyncStorage.getItem(LANGUAGE_STORAGE_KEY);
    
    if (savedLanguage && this.isSupported(savedLanguage)) {
      this.currentLanguage = savedLanguage as SupportedLanguage;
    } else {
      // Use device language if supported
      const deviceLanguage = Localization.locale.split('-')[0];
      if (this.isSupported(deviceLanguage)) {
        this.currentLanguage = deviceLanguage as SupportedLanguage;
      }
    }
  }

  isSupported(lang: string): boolean {
    return ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar'].includes(lang);
  }

  async setLanguage(lang: SupportedLanguage) {
    this.currentLanguage = lang;
    await AsyncStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
  }

  getLanguage(): SupportedLanguage {
    return this.currentLanguage;
  }

  t(key: string): string {
    const translation = translations[this.currentLanguage][key];
    return translation || key;
  }

  getSupportedLanguages(): Array<{ code: SupportedLanguage; name: string; nativeName: string }> {
    return [
      { code: 'en', name: 'English', nativeName: 'English' },
      { code: 'es', name: 'Spanish', nativeName: 'Español' },
      { code: 'fr', name: 'French', nativeName: 'Français' },
      { code: 'de', name: 'German', nativeName: 'Deutsch' },
      { code: 'zh', name: 'Chinese', nativeName: '中文' },
      { code: 'ja', name: 'Japanese', nativeName: '日本語' },
      { code: 'ar', name: 'Arabic', nativeName: 'العربية' },
    ];
  }
}

export const i18n = new I18n();
export default i18n;
