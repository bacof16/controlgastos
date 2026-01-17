'use client';

import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

interface Company {
  id: string;
  name: string;
  is_active: boolean;
}

interface Template {
  id: string;
  title: string;
  company_id: string;
  installment_amount: number;
}

export default function ServicesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  // New Template Form
  const [newTitle, setNewTitle] = useState('');
  const [newAmount, setNewAmount] = useState('');
  
  // Pay Service Form
  const [payTemplateId, setPayTemplateId] = useState<string | null>(null);
  const [payAmount, setPayAmount] = useState('');
  const [payDate, setPayDate] = useState('');

  useEffect(() => {
    loadInitial();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
        loadTemplates(selectedCompany);
    }
  }, [selectedCompany]);

  async function loadInitial() {
    try {
        const res = await fetchApi<Company[]>('/companies/');
        if (res.data && res.data.length > 0) {
            setCompanies(res.data);
            setSelectedCompany(res.data[0].id);
        } else {
            // Should create default if none
            const defRes = await fetchApi<{id:string; name:string}>('/payments/setup/default-company');
            if (defRes.data) {
                 setCompanies([{id: defRes.data.id, name: defRes.data.name || 'Default', is_active: true}]);
                 setSelectedCompany(defRes.data.id);
            }
        }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function loadTemplates(coId: string) {
    const res = await fetchApi<Template[]>(`/recurring/company/${coId}`);
    if (res.data) setTemplates(res.data);
  }

  async function handleCreateTemplate(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCompany) return;

    const res = await fetchApi('/recurring/', {
        method: 'POST',
        body: JSON.stringify({
            company_id: selectedCompany,
            title: newTitle,
            total_installments: 120, // Indefinite 10 years
            installment_amount: parseFloat(newAmount || '0'), 
            start_control_date: new Date().toISOString().split('T')[0],
            autopay_enabled: false
        })
    });

    if (res.status === 200) {
        alert('Servicio Creado');
        setNewTitle('');
        setNewAmount('');
        loadTemplates(selectedCompany);
    }
  }

  async function handlePayService(e: React.FormEvent) {
    e.preventDefault();
    if (!payTemplateId || !selectedCompany) return;

    // Create payment linked to company (and ideally template, but keeping simple for now)
    // We treat this as a "Variable Payment" for the service
    const res = await fetchApi('/payments/', {
        method: 'POST',
        body: JSON.stringify({
            company_id: selectedCompany,
            amount: parseFloat(payAmount),
            due_date: payDate,
            payment_method: 'Manual/Variable',
            status: 'pending',
            payment_reference: 'Pago de Servicio: ' + templates.find(t => t.id === payTemplateId)?.title
        })
    });

    if (res.status === 200) {
        alert('Pago Generado Correctamente');
        setPayTemplateId(null);
        setPayAmount('');
        setPayDate('');
    }
  }

  if (loading) return <div className="container" style={{marginTop: '2rem'}}>Cargando...</div>;

  return (
    <div>
      <header style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
            <h2 className="gradient-text" style={{ fontSize: '2rem' }}>Gestión de Servicios</h2>
            <p style={{ opacity: 0.7 }}>Administra pagos recurrentes y centros de costo.</p>
        </div>
        
        <div style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem 1rem', borderRadius: '8px' }}>
            <span style={{ fontSize: '0.8rem', marginRight: '0.5rem', opacity: 0.8 }}>Centro de Costo:</span>
            <select 
                value={selectedCompany} 
                onChange={e => setSelectedCompany(e.target.value)}
                style={{ background: 'transparent', color: 'white', border: 'none', fontWeight: 'bold' }}
            >
                {companies.map(c => <option key={c.id} value={c.id} style={{color:'black'}}>{c.name}</option>)}
            </select>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        
        {/* Create Service */}
        <div className="glass" style={{ padding: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Nuevo Servicio</h3>
            <form onSubmit={handleCreateTemplate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Nombre</label>
                    <input type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder="Ej. Internet Hogar" style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid #333', background: 'rgba(0,0,0,0.2)', color: 'white' }} required />
                </div>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Costo Estimado</label>
                    <input type="number" value={newAmount} onChange={e => setNewAmount(e.target.value)} placeholder="0.00" style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid #333', background: 'rgba(0,0,0,0.2)', color: 'white' }} />
                </div>
                <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>Crear Servicio</button>
            </form>
        </div>

        {/* List Services */}
        <div className="glass" style={{ padding: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Mis Servicios Activos</h3>
            {templates.length === 0 ? <p style={{opacity:0.5}}>No hay servicios configurados.</p> : (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {templates.map(t => (
                        <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                            <div>
                                <h4 style={{ margin: 0 }}>{t.title}</h4>
                                <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>Estimado: ${t.installment_amount}</span>
                            </div>
                            <button 
                                onClick={() => { setPayTemplateId(t.id); setPayAmount(t.installment_amount.toString()); }}
                                className="btn"
                                style={{ background: 'hsl(var(--success))', fontSize: '0.8rem', padding: '0.4rem 1rem' }}
                            >
                                Pagar Mes
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
      </div>

      {/* Payment Modal Overlay */}
      {payTemplateId && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
            <div className="glass" style={{ padding: '2rem', width: '100%', maxWidth: '400px' }}>
                <h3 style={{ marginBottom: '1.5rem' }}>Registrar Pago Variable</h3>
                <p style={{ marginBottom: '1rem', opacity: 0.7 }}>
                    Servicio: <strong>{templates.find(t => t.id === payTemplateId)?.title}</strong>
                </p>
                <form onSubmit={handlePayService} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Monto Real a Pagar</label>
                        <input type="number" value={payAmount} onChange={e => setPayAmount(e.target.value)} style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid #333', background: 'rgba(0,0,0,0.2)', color: 'white' }} required />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Fecha Vencimiento</label>
                        <input type="date" value={payDate} onChange={e => setPayDate(e.target.value)} style={{ width: '100%', padding: '0.8rem', borderRadius: '8px', border: '1px solid #333', background: 'rgba(0,0,0,0.2)', color: 'white' }} required />
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                        <button type="button" onClick={() => setPayTemplateId(null)} className="btn" style={{ background: 'transparent', border: '1px solid #666', flex: 1 }}>Cancelar</button>
                        <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Confirmar</button>
                    </div>
                </form>
            </div>
        </div>
      )}
    </div>
  );
}
