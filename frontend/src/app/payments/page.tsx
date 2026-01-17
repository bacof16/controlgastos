'use client';

import { useEffect, useState } from 'react';
import { fetchApi } from '../../lib/api';

interface Company {
  id: string;
  name: string;
}

interface Payment {
  id: string;
  amount: number;
  due_date: string;
  payment_method?: string;
  status: string;
  installment_number?: number;
  installment_total?: number;
  payment_reference?: string;
  company_id: string;
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [amount, setAmount] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [issueDate, setIssueDate] = useState(new Date().toISOString().split('T')[0]);
  const [method, setMethod] = useState('Efectivo');
  const [reference, setReference] = useState('');
  const [isInstallment, setIsInstallment] = useState(false);
  const [instTotal, setInstTotal] = useState(1);
  const [status, setStatus] = useState('pending');

  const paymentMethods = [
    'Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia', 'Cheque', 'Otro'
  ];

  useEffect(() => {
    loadInitial();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      loadPayments(selectedCompany);
    }
  }, [selectedCompany]);

  async function loadInitial() {
    try {
        const coRes = await fetchApi<Company[]>('/companies/');
        if (coRes.data && coRes.data.length > 0) {
            setCompanies(coRes.data);
            setSelectedCompany(coRes.data[0].id);
        } else {
            const defRes = await fetchApi<{id:string; name:string}>('/payments/setup/default-company');
            if (defRes.data) {
                setCompanies([{id: defRes.data.id, name: defRes.data.name || 'Default'}]);
                setSelectedCompany(defRes.data.id);
            }
        }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function loadPayments(coId: string) {
    const res = await fetchApi<Payment[]>(`/payments/company/${coId}`);
    if (res.data) setPayments(res.data);
  }

      
    async function deletePayment(id: string) {
        if(!confirm('¿Estás seguro de eliminar este pago?')) return;
        try {
            const res = await fetchApi(`/payments/${id}`, { method: 'DELETE' });
            if (res.status === 200) {
                alert('Pago eliminado.');
                loadPayments(selectedCompany);
            } else {
                alert('Error al eliminar.');
            }
        } catch(e) { console.error(e); }
    }
    
    async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCompany) {
        alert('⚠️ Error: Selecciona una Entidad arriba.');
        return;
    }
    if (!reference.trim()) {
        alert('⚠️ Falta la Empresa/Concepto.');
        return;
    }
    if (!amount || parseFloat(amount) <= 0) {
        alert('⚠️ Monto inválido.');
        return;
    }
    if (!dueDate) {
        alert('⚠️ Falta la Fecha de Vencimiento.');
        return;
    }

    try {
        const finalRef = `${reference} [Emisión: ${issueDate}]`;
        
        const payload = {
            company_id: selectedCompany,
            amount: parseFloat(amount),
            due_date: dueDate,
            payment_method: method,
            payment_reference: finalRef,
            status: status,
            installment_number: isInstallment ? 1 : null,
            installment_total: isInstallment ? instTotal : null,
            autopay: false
        };

        const res = await fetchApi('/payments/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (res.status === 200) {
            alert('¡Operación Exitosa! ✅');
            loadPayments(selectedCompany);
            setAmount('');
            setReference('');
            setIsInstallment(false);
        } else {
            console.error('Backend Error:', res);
            let errMsg = 'Error Desconocido';
            try {
                const errJson = await res.json();
                errMsg = JSON.stringify(errJson, null, 2);
            } catch(e) { errMsg = res.statusText; }
            alert(`❌ Error (${res.status}): ${errMsg}`);
        }
    } catch (err) {
        console.error("Net Error:", err);
        alert('❌ Error de Red.');
    }
  }

  if (loading) return <div className="container" style={{marginTop: '2rem'}}>Cargando...</div>;

  return (
    <div>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
            <h2 className="gradient-text" style={{ fontSize: '2rem' }}>Gestión Financiera</h2>
            <p style={{ opacity: 0.7 }}>Registro detallado de obligaciones y tesorería.</p>
        </div>
        
        <div style={{ background: 'rgba(255,255,255,0.1)', padding: '0.5rem 1rem', borderRadius: '8px' }}>
            <span style={{ fontSize: '0.8rem', marginRight: '0.5rem', opacity: 0.8 }}>Entidad:</span>
            <select 
                value={selectedCompany} 
                onChange={e => setSelectedCompany(e.target.value)}
                style={{ background: 'transparent', color: 'white', border: 'none', fontWeight: 'bold' }}
            >
                {companies.map(c => <option key={c.id} value={c.id} style={{color:'black'}}>{c.name}</option>)}
            </select>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem' }}>
        
        {/* Enterprise Form */}
        <div className="glass" style={{ padding: '2rem', height: 'fit-content' }}>
            <h3 style={{ marginBottom: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem' }}>Nueva Obligación</h3>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                
                
                {/* Invoice Date Row */}
                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.3rem', opacity: 0.8 }}>Fecha de Emisión (Factura)</label>
                    <input type="date" value={issueDate} onChange={e => setIssueDate(e.target.value)} 
                           style={{ width: '100%', padding: '0.8rem', borderRadius: '6px', border: '1px solid #444', background: 'rgba(0,0,0,0.3)', color: 'white' }} />
                </div>
{/* Hero Amount Input */}
                <div style={{ marginBottom: '1.5rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '12px', border: '1px solid #333' }}>
                    <label style={{ display: 'block', fontSize: '0.9rem', marginBottom: '0.5rem', color: '#aaa' }}>Monto a Pagar</label>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '2rem', marginRight: '0.5rem', color: '#4caf50' }}>$</span>
                        <input 
                            type="number" 
                            step="0.01" 
                            value={amount} 
                            onChange={e => setAmount(e.target.value)} 
                            required 
                            placeholder="0.00"
                            style={{ 
                                flex: 1, 
                                minWidth: '200px',
                                background: 'transparent', 
                                border: 'none', 
                                fontSize: '3rem', 
                                fontWeight: 'bold', 
                                color: '#ffffff', 
                                outline: 'none',
                                padding: '0.5rem',
                                zIndex: 10
                            }} 
                        />
                    </div>
                </div>

                {/* Date Selection */}
                <div style={{ marginBottom: '1rem' }}>                    <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.3rem', opacity: 0.8 }}>Vencimiento</label>
                    <div style={{display: 'flex', gap: '0.5rem'}}>
                        <input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} required 
                            style={{ flex: 1, padding: '0.8rem', borderRadius: '6px', border: '1px solid #444', background: 'rgba(0,0,0,0.3)', color: 'white' }} />
                        <button type="button" onClick={() => {
                            const d = new Date(); d.setDate(d.getDate() + 30); 
                            setDueDate(d.toISOString().split('T')[0]);
                        }} style={{padding: '0 1rem', background: '#333', border: '1px solid #555', borderRadius: '6px', cursor: 'pointer', color: 'white'}}>+30d</button>
                         <button type="button" onClick={() => {
                            const d = new Date(); d.setDate(d.getDate() + 7); 
                            setDueDate(d.toISOString().split('T')[0]);
                        }} style={{padding: '0 1rem', background: '#333', border: '1px solid #555', borderRadius: '6px', cursor: 'pointer', color: 'white'}}>+7d</button>
                    </div>
                </div>

                {/* Method */}
                <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.3rem', opacity: 0.8 }}>Método de Pago</label>
                    <select value={method} onChange={e => setMethod(e.target.value)} 
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '6px', border: '1px solid #444', background: 'rgba(0,0,0,0.3)', color: 'white' }}>
                        {paymentMethods.map(m => <option key={m} value={m} style={{color:'black'}}>{m}</option>)}
                    </select>
                </div>

                {/* Installments Toggle */}
                <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.8rem', borderRadius: '6px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <label style={{ fontSize: '0.9rem' }}>¿Compra en Cuotas?</label>
                        <input type="checkbox" checked={isInstallment} onChange={e => setIsInstallment(e.target.checked)} style={{transform: 'scale(1.2)'}} />
                    </div>
                    {isInstallment && (
                        <div style={{ marginTop: '0.8rem' }}>
                            <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.3rem', opacity: 0.8 }}>Cantidad de Cuotas</label>
                            <input type="number" min="2" max="60" value={instTotal} onChange={e => setInstTotal(parseInt(e.target.value))} 
                                style={{ width: '100%', padding: '0.6rem', borderRadius: '4px', border: '1px solid #555', background: 'black', color: 'white' }} />
                        </div>
                    )}
                </div>

                {/* Status & Reference */}
                <div>
                    <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.3rem', opacity: 0.8 }}>Nombre de la Deuda / Empresa (Ej. Fibertel)</label>
                    <input type="text" required placeholder="Ingresa el nombre aquí..." value={reference} onChange={e => setReference(e.target.value)} 
                        style={{ width: '100%', padding: '0.8rem', borderRadius: '6px', border: '1px solid #444', background: 'rgba(0,0,0,0.3)', color: 'white', fontFamily: 'inherit' }} />
                </div>

                <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem', padding: '1rem', fontWeight: 'bold', letterSpacing: '1px' }}>
                    REGISTRAR OPERACIÓN
                </button>
            </form>
        </div>

        {/* Data Grid */}
        <div className="glass" style={{ padding: '2rem', overflowX: 'auto' }}>
            <h3 style={{ marginBottom: '1.5rem' }}>Últimos Movimientos</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
                <thead>
                    <tr style={{textAlign: 'left', borderBottom: '2px solid rgba(255,255,255,0.1)', fontSize: '0.8rem', opacity: 0.7, textTransform: 'uppercase'}}>
                        <th style={{padding: '1rem'}}>Fecha</th>
                        <th style={{padding: '1rem'}}>Concepto/Ref</th>
                        <th style={{padding: '1rem'}}>Método</th>
                        <th style={{padding: '1rem'}}>Cuota</th>
                        <th style={{padding: '1rem', textAlign: 'right'}}>Monto</th>
                        <th style={{padding: '1rem'}}>Estado</th><th style={{padding: '1rem', textAlign: 'center'}}>borrar</th><th style={{padding: '1rem'}}>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {payments.length === 0 && (
                        <tr><td colSpan={6} style={{padding:'2rem', textAlign:'center', opacity: 0.5}}>No hay registros contables.</td></tr>
                    )}
                    {payments.map(p => (
                        <tr key={p.id} style={{borderBottom: '1px solid rgba(255,255,255,0.05)'}}>
                            <td style={{padding: '1rem', fontSize: '0.9rem'}}>{new Date(p.due_date).toLocaleDateString()}</td>
                            <td style={{padding: '1rem', fontSize: '0.9rem'}}>{p.payment_reference || 'Sin referencia'}</td>
                            <td style={{padding: '1rem', fontSize: '0.8rem'}}>{p.payment_method || '-'}</td>
                            <td style={{padding: '1rem', fontSize: '0.8rem'}}>{p.installment_total ? `${p.installment_number}/${p.installment_total}` : 'Unico'}</td>
                            <td style={{padding: '1rem', textAlign: 'right', fontWeight: 'bold'}}>${Number(p.amount).toFixed(2)}</td>
                            <td style={{padding: '1rem'}}>
                                <span style={{
                                    padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold', textTransform: 'uppercase',
                                    border: `1px solid ${p.status === 'paid' ? '#4caf50' : '#ff9800'}`,
                                    color: p.status === 'paid' ? '#4caf50' : '#ff9800'
                                }}>
                                    {p.status}
                                </span>
                            </td>
                            <td style={{padding: '1rem', textAlign: 'center'}}>
                                <button onClick={() => deletePayment(p.id)} style={{background: 'none', border: 'none', cursor: 'pointer'}}>❌</button>
                            </td>

                            <td style={{padding: '1rem', textAlign: 'center'}}>
                                <button onClick={() => deletePayment(p.id)} style={{
                                    background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '1.2rem'
                                }}>🗑️</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>

      </div>
    </div>
  );
}
