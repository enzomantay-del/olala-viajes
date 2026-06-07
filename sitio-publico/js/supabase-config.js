// Misma cuenta Supabase que Jardín Sale Week (solo clave pública anon).
window.SUPABASE_URL = 'https://ldtfdsipdjrmcgcsbrfc.supabase.co';
window.SUPABASE_ANON_KEY = 'sb_publishable_2wEXxWy-JQWQAEKE4NCPjQ_7XFhsQ4h';

window.OLALA_WHATSAPP = '5493743483429';
window.OLALA_TELEFONO = '+54 9 3743 483429';
window.OLALA_EMAIL = 'enzomantay@gmail.com';
window.OLALA_PANEL_URL = 'http://127.0.0.1:8000/accounts/login/';

window.getSupabaseClient = function getSupabaseClient() {
  if (!window.supabase || !window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
    return null;
  }
  return window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
};
