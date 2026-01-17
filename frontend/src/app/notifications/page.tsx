'use client';

import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

interface Notification {
  id: string;
  channel: string;
  status: string;
  created_at: string;
  payload: any;
}

export default function NotificationsPage() {
  const [list, setList] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
        const res = await fetchApi<Notification[]>('/notifications/queue?limit=20');
        if (res.data) setList(res.data);
    } catch (e) {
        console.error(e);
    } finally {
        setLoading(false);
    }
  }

  async function handleRetry(id: string) {
    const res = await fetchApi(`/notifications/queue/${id}/retry`, { method: 'POST' });
    if (res.status === 200) {
        alert('Reintentando...');
        loadData();
    }
  }

  return (
    <div>
        <header style={{ marginBottom: '3rem' }}>
            <h2 className="gradient-text" style={{ fontSize: '2rem' }}>Historial de Alertas</h2>
            <p style={{ opacity: 0.7 }}>Registro de notificaciones enviadas por el sistema.</p>
        </header>

        <div className="glass" style={{ padding: '2rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)'}}>
                        <th style={{padding: '1rem'}}>Fecha</th>
                        <th style={{padding: '1rem'}}>Canal</th>
                        <th style={{padding: '1rem'}}>Mensaje</th>
                        <th style={{padding: '1rem'}}>Estado</th>
                        <th style={{padding: '1rem'}}>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {list.map(n => (
                        <tr key={n.id} style={{borderBottom: '1px solid rgba(255,255,255,0.05)'}}>
                            <td style={{padding: '1rem', fontSize: '0.9rem'}}>{new Date(n.created_at).toLocaleString()}</td>
                            <td style={{padding: '1rem', textTransform: 'capitalize'}}>{n.channel}</td>
                            <td style={{padding: '1rem', fontSize: '0.9rem', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                                {n.payload.message || JSON.stringify(n.payload)}
                            </td>
                            <td style={{padding: '1rem'}}>
                                <span style={{
                                    padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold',
                                    backgroundColor: n.status === 'sent' ? 'rgba(0, 255, 0, 0.1)' : n.status === 'failed' ? 'rgba(255, 0, 0, 0.1)' : 'rgba(255, 255, 0, 0.1)',
                                    color: n.status === 'sent' ? '#4caf50' : n.status === 'failed' ? '#ff5252' : '#ffeb3b'
                                }}>
                                    {n.status.toUpperCase()}
                                </span>
                            </td>
                            <td style={{padding: '1rem'}}>
                                {n.status === 'failed' && (
                                    <button onClick={() => handleRetry(n.id)} style={{
                                        background: 'transparent', border: '1px solid white', color: 'white', 
                                        padding: '0.3rem 0.8rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem'
                                    }}>
                                        Reintentar
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {list.length === 0 && <p style={{textAlign: 'center', marginTop: '2rem', opacity: 0.5}}>No hay notificaciones recientes.</p>}
        </div>
    </div>
  );
}
