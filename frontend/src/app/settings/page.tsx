'use client';

import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

interface Settings {
  id: string;
  telegram_enabled: boolean;
  email_enabled: boolean;
  telegram_chat_id?: string;
  email_address?: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [companyId, setCompanyId] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
        const compRes = await fetchApi<{id: string}>('/payments/setup/default-company');
        if (compRes.data) {
            setCompanyId(compRes.data.id);
            const setRes = await fetchApi<Settings>(`/notifications/settings/company/${compRes.data.id}`);
            if (setRes.data) {
                setSettings(setRes.data);
            } else {
                // If 404, maybe create default settings? For now assume manual endpoint creation or handle error
            }
        }
    } catch (e) {
        console.error(e);
    } finally {
        setLoading(false);
    }
  }

  async function handleToggle(field: 'telegram_enabled' | 'email_enabled') {
    if (!settings) return;
    const newVal = !settings[field];
    
    // Optimistic update
    setSettings({...settings, [field]: newVal});

    await fetchApi(`/notifications/settings/${settings.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ [field]: newVal })
    });
  }

  if (loading) return <div className="container" style={{ marginTop: '2rem' }}>Cargando...</div>;

  if (!settings) return (
    <div className="container" style={{ marginTop: '3rem' }}>
        <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}>
            <h3>No se encontró configuración</h3>
            <p>Por favor contacta al administrador o crea la configuración inicial vía API.</p>
        </div>
    </div>
  );

  return (
    <div>
        <header style={{ marginBottom: '3rem' }}>
            <h2 className="gradient-text" style={{ fontSize: '2rem' }}>Configuración</h2>
            <p style={{ opacity: 0.7 }}>Gestiona tus canales de notificación.</p>
        </header>

        <div className="glass" style={{ padding: '2rem', maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <div>
                    <h3 style={{ fontSize: '1.1rem' }}>Telegram</h3>
                    <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>Recibe alertas instántaneas en tu móvil</p>
                </div>
                <label className="switch">
                    <input type="checkbox" checked={settings.telegram_enabled} onChange={() => handleToggle('telegram_enabled')} />
                    <span className="slider round"></span>
                </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h3 style={{ fontSize: '1.1rem' }}>Email</h3>
                    <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>Resúmenes semanales y alertas críticas</p>
                </div>
                <label className="switch">
                    <input type="checkbox" checked={settings.email_enabled} onChange={() => handleToggle('email_enabled')} />
                    <span className="slider round"></span>
                </label>
            </div>
        </div>

        <style jsx>{`
            .switch { position: relative; display: inline-block; width: 50px; height: 26px; }
            .switch input { opacity: 0; width: 0; height: 0; }
            .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
            .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
            input:checked + .slider { background-color: #2196F3; }
            input:checked + .slider:before { transform: translateX(24px); }
        `}</style>
    </div>
  );
}
