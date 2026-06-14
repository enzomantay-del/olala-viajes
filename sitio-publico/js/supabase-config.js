// Misma cuenta Supabase que Jardín Sale Week (solo clave pública anon).
window.SUPABASE_URL = 'https://ldtfdsipdjrmcgcsbrfc.supabase.co';
window.SUPABASE_ANON_KEY = 'sb_publishable_2wEXxWy-JQWQAEKE4NCPjQ_7XFhsQ4h';

window.OLALA_WHATSAPP = '5493743483429';
window.OLALA_TELEFONO = '+54 9 3743 483429';
window.OLALA_EMAIL = 'enzomantay@gmail.com';
// Panel en internet (Render). En tu PC también podés usar iniciar-panel.bat → localhost:8000
window.OLALA_PANEL_URL = 'https://olala-viajes.onrender.com/accounts/login/';
window.OLALA_COTIZAR_URL = 'https://olala-viajes.onrender.com/web/cotizar/';
window.OLALA_ALERTA_URL = 'https://olala-viajes.onrender.com/web/alerta/';

window.getSupabaseClient = function getSupabaseClient() {
  if (!window.supabase || !window.SUPABASE_URL || !window.SUPABASE_ANON_KEY) {
    return null;
  }
  return window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
};
