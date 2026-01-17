'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '../../lib/api';

import PaymentModal from '../../components/PaymentModal';

// --- Helpers ---
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount);
};


// --- Types ---
interface Company { id: string; name: string; }
interface Payment {
  id: string; 
  amount: number; 
  due_date: string; 
  status: string; 
  payment_reference?: string;
  payment_method?: string;
  category?: string; // Missing in backend currently, using basic logic
}

export default function DashboardPage() {
  const router = useRouter();
  
  // --- Global State ---
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [profileMode, setProfileMode] = useState<'Personal' | 'Cronet'>('Personal');
  
  // --- Data State ---
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [editingPayment, setEditingPayment] = useState<Payment | null>(null);
  const [viewMode, setViewMode] = useState<'dashboard' | 'payments' | 'alerts' | 'services' | 'config'>('dashboard');
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);

  // --- Init ---
  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (selectedCompany) loadPayments();
  }, [selectedCompany, currentDate]);

  // --- Logic ---
  async function loadCompanies() {
    try {
        const res = await fetchApi<Company[]>('/companies/');
        if (res.data) {
            setCompanies(res.data);
            // Default to Personal or first
            const personal = res.data.find(c => c.name.includes('Personal'));
            if(personal) setSelectedCompany(personal.id);
            else if(res.data.length > 0) setSelectedCompany(res.data[0].id);
        }
    } catch(e) { console.error(e); }
  }

  async function loadPayments() {
    // In real app, filter by month/year in backend. Here client-side filter.
    if(!selectedCompany) return;
    setLoading(true);
    try {
        const res = await fetchApi<Payment[]>(`/payments/company/${selectedCompany}`);
        if(res.data) {


            // Filter by Month
            
            // Category Extraction (Global)
            const cats = Array.from(new Set([
                'General', 'Servicios', 'Hogar', 'Oficina', 'Personal', 'Comida', 'Transporte', 'Salud', 'Educación', 'Entretenimiento',
                ...res.data.map(p => p.category || 'General')
            ])).sort();
            setAvailableCategories(cats);

            const filtered = res.data.filter(p => {
                const d = new Date(p.due_date);
                return d.getMonth() === currentDate.getMonth() && d.getFullYear() === currentDate.getFullYear();
            });
            setPayments(filtered);
        }
    } catch(e) { console.error(e); }
    finally { setLoading(false); }
  }

  
  // --- Selection Handlers ---
  function toggleSelection(id: string) {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedIds(newSet);
  }

  function toggleAll() {
    if (selectedIds.size === payments.length) {
        setSelectedIds(new Set());
    } else {
        setSelectedIds(new Set(payments.map(p => p.id)));
    }
  }

  async function handleBulkDelete() {
    if (!confirm(`¿Eliminar ${selectedIds.size} registros?`)) return;
    
    setLoading(true);
    try {
        // Parallel deletes
        await Promise.all(
            Array.from(selectedIds).map(id => 
                fetchApi(`/payments/${id}`, { method: 'DELETE' })
            )
        );
        setSelectedIds(new Set());
        loadPayments(); // Reload
    } catch (e) { console.error(e); alert('Error eliminando'); }
    // Loading set false by loadPayments
  }

  function handleMonthChange(delta: number) {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + delta);
    setCurrentDate(newDate);
  }

  function toggleProfile() {
    const newMode = profileMode === 'Personal' ? 'Cronet' : 'Personal';
    setProfileMode(newMode);
    // Find ID
    const target = companies.find(c => c.name.includes(newMode));
    if(target) setSelectedCompany(target.id);
  }

  
  

  // --- KPI Calcs ---
  const totalPending = payments.filter(p => p.status !== 'paid').reduce((acc, p) => acc + Number(p.amount), 0);
  const totalPaid = payments.filter(p => p.status === 'paid').reduce((acc, p) => acc + Number(p.amount), 0);
  const overdueCount = payments.filter(p => p.status === 'overdue' || (p.status !== 'paid' && new Date(p.due_date) < new Date())).length;

  // --- Render Helpers ---
  const monthName = currentDate.toLocaleString('es-ES', { month: 'long', year: 'numeric' }).toUpperCase();

  return (
    <div style={{ minHeight: '100vh', background: '#050505', color: '#e0e0e0', fontFamily: 'Inter, sans-serif' }}>
      
      {/* 1.1 Navbar */}
      <nav style={{ 
        display: 'flex', flexDirection: 'column',
        background: 'rgba(5,5,5,0.95)', borderBottom: '1px solid #222', 
        position: 'sticky', top: 0, zIndex: 100 
      }}>
        {/* Top Level: Logo & Main Links */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 2rem', borderBottom: '1px solid #1a1a1a' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', background: 'linear-gradient(to right, #3b82f6, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                ControlGastos
            </div>
            
            <div style={{ display: 'flex', gap: '2rem' }}>
                <NavLink active={viewMode === 'dashboard'} onClick={() => setViewMode('dashboard')}>Dashboard</NavLink>
                <NavLink active={viewMode === 'payments'} onClick={() => setViewMode('payments')}>Pagos</NavLink>
                <NavLink active={viewMode === 'alerts'} onClick={() => alert('Próximamente: Vista de Alertas')}>Alertas</NavLink>
                <NavLink active={viewMode === 'services'} onClick={() => alert('Próximamente: Gestión de Servicios')}>Servicios</NavLink>
                <NavLink active={viewMode === 'config'} onClick={() => alert('Próximamente: Configuración Global')}>Configuración</NavLink>
            </div>
        </div>

        {/* Second Level: Context Controls (Date & Profile) */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.8rem 2rem', background: '#0a0a0a' }}>
            {/* Date Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <button onClick={() => handleMonthChange(-1)} style={navBtnStyle}>&lt;</button>
                <span style={{ fontSize: '1.1rem', fontWeight: 'bold', minWidth: '180px', textAlign: 'center', color: 'white' }}>{monthName}</span>
                <button onClick={() => handleMonthChange(1)} style={navBtnStyle}>&gt;</button>
            </div>

            {/* Profile & Logout */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div style={{ background: '#1a1a1a', borderRadius: '20px', padding: '4px', display: 'flex', border: '1px solid #333' }}>
                    <button 
                        onClick={() => profileMode !== 'Personal' && toggleProfile()}
                        style={{ ...pillStyle, background: profileMode === 'Personal' ? '#3b82f6' : 'transparent', color: profileMode === 'Personal' ? 'white' : '#888' }}
                    >Personal</button>
                    <button 
                        onClick={() => profileMode !== 'Cronet' && toggleProfile()}
                        style={{ ...pillStyle, background: profileMode === 'Cronet' ? '#8b5cf6' : 'transparent', color: profileMode === 'Cronet' ? 'white' : '#888' }}
                    >Cronet</button>
                </div>
                
                <button onClick={() => router.push('/login')} style={{ 
                    color: '#666', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.9rem',
                    display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'color 0.2s'
                }}
                onMouseEnter={e => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={e => e.currentTarget.style.color = '#666'}
                >
                    Cerrar Sesión
                </button>
            </div>
        </div>
      </nav>

      <main style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
{viewMode === 'dashboard' && (<>
        
        {/* 1.2 KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
            <KpiCard title="POR PAGAR" amount={totalPending} color="#fbbf24" label="Pendientes" />
            <KpiCard title="PAGADO MES" amount={totalPaid} color="#34d399" label="Ejecutado" />
            <div style={cardStyle}>
                <h3 style={{ fontSize: '0.8rem', color: '#888', marginBottom: '0.5rem', textTransform: 'uppercase' }}>ALERTAS</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ 
                        width: '40px', height: '40px', borderRadius: '50%', 
                        background: overdueCount > 0 ? '#ef4444' : '#34d399',
                        boxShadow: overdueCount > 0 ? '0 0 15px rgba(239, 68, 68, 0.4)' : '0 0 15px rgba(52, 211, 153, 0.4)'
                    }} />
                    <div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>{overdueCount > 0 ? 'Atención' : 'Al Día'}</div>
                        <div style={{ fontSize: '0.9rem', color: '#888' }}>{overdueCount} pagos vencidos</div>
                    </div>
                </div>
            </div>
        </div>

        {/* 1.3 Action Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem' }}>
                <ActionButton label="Centros de Costo" />
                <ActionButton label="Cuentas" />
                <ActionButton label="Auditoría" />
            </div>
            
            <button onClick={() => { setEditingPayment(null); setIsModalOpen(true); }} style={{ 
                background: '#2563eb', color: 'white', border: 'none', padding: '0.8rem 1.5rem', borderRadius: '8px', 
                fontWeight: 'bold', cursor: 'pointer', boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.2)' 
            }}>
                + NUEVO REGISTRO
            </button>
        </div>

        {/* Tools Bar */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', background: '#111', padding: '1rem', borderRadius: '12px', border: '1px solid #222' }}>
            <input type="text" placeholder="Buscar por nombre, nota..." style={inputStyle} />
            <select style={inputStyle}><option>Todas las Categorías</option></select>
            <div style={{ flex: 1 }} />
            <button style={secondaryBtnStyle}>Columnas</button>
            <button style={secondaryBtnStyle}>Exportar Excel</button>
        </div>

        {/* 1.4 Main Table */}
        <div style={{ background: '#111', borderRadius: '12px', border: '1px solid #222', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                    <tr style={{ background: '#1a1a1a', borderBottom: '1px solid #333', textAlign: 'left', color: '#888' }}>
                        <th style={{ padding: '1rem' }}><input type="checkbox" checked={payments.length > 0 && selectedIds.size === payments.length} onChange={toggleAll} /></th>
                        <th style={{ padding: '1rem' }}>FECHA</th>
                        <th style={{ padding: '1rem' }}>ITEM</th>
                        <th style={{ padding: '1rem' }}>CATEGORÍA</th>
                        <th style={{ padding: '1rem' }}>REFERENCIA</th>
                        <th style={{ padding: '1rem', textAlign: 'right' }}>MONTO</th>
                        <th style={{ padding: '1rem', textAlign: 'center' }}>ESTADO</th>
                        <th style={{ padding: '1rem' }}>ACCIONES</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr><td colSpan={8} style={{ padding: '3rem', textAlign: 'center', color: '#666' }}>Cargando datos financieros...</td></tr>
                    ) : payments.length === 0 ? (
                        <tr><td colSpan={8} style={{ padding: '3rem', textAlign: 'center', color: '#666' }}>No hay registros para este mes.</td></tr>
                    ) : (
                        payments.map(p => (
                            <tr key={p.id} style={{ borderBottom: '1px solid #222', transition: 'background 0.2s' }} 
                                onMouseEnter={(e) => e.currentTarget.style.background = '#1f1f1f'}
                                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            >
                                <td style={{ padding: '1rem' }}><input type="checkbox" checked={selectedIds.has(p.id)} onChange={() => toggleSelection(p.id)} /></td>
                                <td style={{ padding: '1rem', color: '#ccc' }}>{new Date(p.due_date).toLocaleDateString()}</td>
                                <td style={{ padding: '1rem', fontWeight: 'bold', color: 'white' }}>{p.payment_reference?.split('[')[0] || 'Gasto General'}</td>
                                <td style={{ padding: '1rem', color: '#888' }}>{p.category || 'General'}</td>
                                <td style={{ padding: '1rem', fontStyle: 'italic', color: '#666' }}>{p.payment_reference}</td>
                                <td style={{ padding: '1rem', textAlign: 'right', fontWeight: 'bold', color: p.status==='paid'?'#34d399':'white' }}>
                                    {formatCurrency(p.amount)}
                                </td>
                                <td style={{ padding: '1rem', textAlign: 'center' }}>
                                    <StatusBadge status={p.status} />
                                </td>
                                <td style={{ padding: '1rem' }}>
                                    <button onClick={() => { setEditingPayment(p); setIsModalOpen(true); }} style={{ background: 'none', border: 'none', cursor: 'pointer', marginRight: '0.5rem' }}>✏️</button>
                                    <button onClick={() => { if(confirm('¿Borrar?')) { fetchApi(`/payments/${p.id}`, {method:'DELETE'}).then(loadPayments); } }} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>🗑️</button>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>

      
        {/* Bulk Action Bar (Floating) */}
        {selectedIds.size > 0 && (
            <div style={{
                position: 'fixed', bottom: '2rem', left: '50%', transform: 'translateX(-50%)',
                background: '#1a1a1a', border: '1px solid #333', borderRadius: '12px', padding: '1rem 2rem',
                display: 'flex', alignItems: 'center', gap: '2rem', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', zIndex: 90
            }}>
                <div style={{ color: 'white', fontWeight: 'bold' }}>{selectedIds.size} seleccionados</div>
                <button onClick={handleBulkDelete} style={{
                    background: '#ef4444', color: 'white', border: 'none', padding: '0.6rem 1.2rem',
                    borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
                }}>
                    Eliminar Selección
                </button>
                <button onClick={() => setSelectedIds(new Set())} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}>
                    Cancelar
                </button>
            </div>
        )}

      </>)}

        {viewMode === 'payments' && (
            <div style={{ animation: 'fadeIn 0.3s' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>Resumen de Pagos Ejecutados</h2>
                <div style={{ background: '#111', borderRadius: '12px', border: '1px solid #222', padding: '2rem' }}>
                    {payments.filter(p => p.status === 'paid').length === 0 ? (
                         <div style={{ textAlign: 'center', color: '#666' }}>No hay pagos ejecutados en este mes.</div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #333', textAlign: 'left', color: '#888' }}>
                                    <th style={{ padding: '1rem' }}>FECHA PAGO</th>
                                    <th style={{ padding: '1rem' }}>ITEM</th>
                                    <th style={{ padding: '1rem' }}>CATEGORÍA</th>
                                    <th style={{ padding: '1rem', textAlign: 'right' }}>MONTO</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payments.filter(p => p.status === 'paid').map(p => (
                                    <tr key={p.id} style={{ borderBottom: '1px solid #222' }}>
                                        <td style={{ padding: '1rem', color: '#ccc' }}>{new Date(p.due_date).toLocaleDateString()}</td>
                                        <td style={{ padding: '1rem', fontWeight: 'bold', color: 'white' }}>{p.payment_reference?.split('[')[0]}</td>
                                        <td style={{ padding: '1rem', color: '#888' }}>{p.category || 'General'}</td>
                                        <td style={{ padding: '1rem', textAlign: 'right', color: '#34d399', fontWeight: 'bold' }}>
                                            {formatCurrency(p.amount)}
                                        </td>
                                    </tr>
                                ))}
                                <tr style={{ borderTop: '2px solid #333' }}>
                                    <td colSpan={3} style={{ padding: '1rem', textAlign: 'right', fontWeight: 'bold', color: 'white' }}>TOTAL PAGADO</td>
                                    <td style={{ padding: '1rem', textAlign: 'right', fontSize: '1.2rem', color: '#34d399', fontWeight: 'bold' }}>
                                        {formatCurrency(payments.filter(p => p.status === 'paid').reduce((acc, p) => acc + Number(p.amount), 0))}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        )}
</main>
      <PaymentModal isOpen={isModalOpen} onClose={() => { setIsModalOpen(false); setEditingPayment(null); }} companyId={selectedCompany} onSave={loadPayments} initialData={editingPayment} availableCategories={availableCategories} />
    </div>
  );
}

// --- Components ---
function NavLink({ children, active, onClick }: any) {
    return (
        <button onClick={onClick} style={{ 
            background: 'none', border: 'none', color: active ? 'white' : '#888', 
            fontSize: '0.95rem', fontWeight: active ? 'bold' : 'normal', cursor: 'pointer',
            padding: '0.5rem 0', borderBottom: active ? '2px solid #3b82f6' : '2px solid transparent'
        }}>
            {children}
        </button>
    );
}


function KpiCard({ title, amount, color, label }: any) {
    return (
        <div style={cardStyle}>
            <h3 style={{ fontSize: '0.8rem', color: '#888', marginBottom: '0.5rem', textTransform: 'uppercase' }}>{title}</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.2rem' }}>
                {new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount)}
            </div>
            <div style={{ fontSize: '0.8rem', color, fontWeight: 'bold' }}>{label}</div>
        </div>
    );
}

function ActionButton({ label, onClick }: any) {
    return (
        <button onClick={onClick} style={{ 
            background: 'rgba(255,255,255,0.05)', color: '#ccc', border: '1px solid #333', 
            padding: '0.5rem 1rem', borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem' 
        }}>
            {label}
        </button>
    );
}

function StatusBadge({ status }: { status: string }) {
    const map: any = {
        paid: { bg: 'rgba(52, 211, 153, 0.1)', col: '#34d399', txt: 'PAGADO' },
        pending: { bg: 'rgba(251, 191, 36, 0.1)', col: '#fbbf24', txt: 'PENDIENTE' },
        overdue: { bg: 'rgba(239, 68, 68, 0.1)', col: '#ef4444', txt: 'VENCIDO' }
    };
    const s = map[status] || map.pending;
    return (
        <span style={{ 
            background: s.bg, color: s.col, padding: '0.25rem 0.75rem', 
            borderRadius: '99px', fontSize: '0.7rem', fontWeight: 'bold', letterSpacing: '0.5px' 
        }}>
            {s.txt}
        </span>
    );
}

// --- Styles ---
const navBtnStyle: any = { background: 'none', border: '1px solid #333', borderRadius: '50%', width: '32px', height: '32px', color: '#ccc', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' };
const pillStyle: any = { border: 'none', padding: '0.4rem 1.2rem', borderRadius: '16px', fontSize: '0.85rem', cursor: 'pointer', transition: 'all 0.2s', fontWeight: '500' };
const cardStyle: any = { background: 'rgba(255,255,255,0.03)', border: '1px solid #222', borderRadius: '16px', padding: '1.5rem', backdropFilter: 'blur(5px)' };
const inputStyle: any = { background: '#0a0a0a', border: '1px solid #333', padding: '0.6rem 1rem', borderRadius: '6px', color: 'white', outline: 'none', minWidth: '200px' };
const secondaryBtnStyle: any = { background: 'transparent', border: '1px solid #333', color: '#888', padding: '0.6rem 1rem', borderRadius: '6px', cursor: 'pointer' };
