'use client';

import { useState, useEffect } from 'react';
import { fetchApi } from '../lib/api';

export default function PaymentModal({ isOpen, onClose, companyId, onSave, initialData, availableCategories = [] }: any) {
  if (!isOpen) return null;

  useEffect(() => {
    if (initialData) {
        setTitle(initialData.payment_reference?.split('[')[0].trim() || ''); // Approximate title extraction
        setAmount(initialData.amount);
        setDueDate(initialData.due_date ? initialData.due_date.split('T')[0] : '');
        setCategory(initialData.category || 'General');
        // We might not have all fields in 'initialData' list view, but it's a start.
        // For full edit, usually we fetch detail. For now, trusting list data.
        if (initialData.payment_reference) {
            const matches = initialData.payment_reference.match(/\(Fac: (.*?)\)/);
            if(matches) setInvoiceNumber(matches[1]);
            const noteMatch = initialData.payment_reference.match(/\[(.*?)\]/);
            if(noteMatch) setNotes(noteMatch[1]);
        }
    } else {
        // Reset
        setTitle(''); setAmount(''); setDueDate(''); setCategory('General');
        setInvoiceNumber(''); setNotes('');
    }
  }, [initialData, isOpen]);


  // --- State ---
  // 2.1 Basics
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('General');
  const [dueDate, setDueDate] = useState('');

  // 2.2 Behavior
  const [type, setType] = useState('Fijo'); // Fijo | Variable
  const [autoPay, setAutoPay] = useState(false);
  const [isInstallment, setIsInstallment] = useState(false);
  const [instCurrent, setInstCurrent] = useState(1);
  const [instTotal, setInstTotal] = useState(12);

  // 2.3 Context
  const [invoiceDate, setInvoiceDate] = useState('');
  const [invoiceNumber, setInvoiceNumber] = useState('');
  const [notes, setNotes] = useState('');

  // 2.4 Allocation
  // (Simplified for now, just placeholders)

  const [loading, setLoading] = useState(false);

  // --- Handlers ---
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if(!companyId) {alert('Error: No company selected'); return;}
    
    setLoading(true);
    try {
        // Construct Reference from Title + Invoice + Notes
        const reference = `${title} ${invoiceNumber ? `(Fac: ${invoiceNumber})` : ''} ${notes ? `[${notes}]` : ''}`.trim();

        const payload = {
            company_id: companyId,
            amount: parseFloat(amount) || 0, // Allow 0
            due_date: dueDate,
            payment_method: 'Pending', // Will be set on Pay
            payment_reference: reference, // Using reference as Title storage for now
            status: 'pending',
            autopay: autoPay,
            installment_number: isInstallment ? instCurrent : null, 
            installment_total: isInstallment ? instTotal : null
        };

        const url = initialData ? `/payments/${initialData.id}` : '/payments/';
        const method = initialData ? 'PUT' : 'POST';
        const res = await fetchApi(url, {
            method: method,
            body: JSON.stringify(payload)
        });

        if (res.status === 200) {
            onSave();
            onClose();
        } else {
            alert('Error creating payment');
        }
    } catch(e) { console.error(e); alert('Network Error'); }
    finally { setLoading(false); }
  }

  // --- Styles ---
  const modalOverlay: any = { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(5px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 };
  const modalContent: any = { background: '#111', border: '1px solid #333', borderRadius: '16px', width: '600px', maxHeight: '90vh', overflowY: 'auto', padding: '2rem', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)' };
  const sectionTitle: any = { fontSize: '0.8rem', color: '#888', textTransform: 'uppercase', marginBottom: '1rem', borderBottom: '1px solid #222', paddingBottom: '0.5rem', marginTop: '1.5rem' };
  const rowStyle: any = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' };
  const inputStyle: any = { width: '100%', padding: '0.8rem', background: '#0a0a0a', border: '1px solid #333', borderRadius: '8px', color: 'white', outline: 'none' };
  const labelStyle: any = { display: 'block', fontSize: '0.8rem', marginBottom: '0.4rem', color: '#ccc' };

  return (
    <div style={modalOverlay} onClick={onClose}>
      <div style={modalContent} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{initialData ? 'Editar Registro' : 'Nuevo Registro'}</h2>
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: '1.5rem' }}>&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
            {/* 2.1 Datos Básicos */}
            <div style={{...sectionTitle, marginTop: 0}}>1. Datos Básicos</div>
            <div style={rowStyle}>
                <div style={{gridColumn: 'span 2'}}>
                    <label style={labelStyle}>Título (Item)</label>
                    <input autoFocus required value={title} onChange={e=>setTitle(e.target.value)} placeholder="Ej: Alquiler Oficina" style={inputStyle} />
                </div>
                <div>
                    <label style={labelStyle}>Monto</label>
                    <div style={{position:'relative'}}>
                        <span style={{position:'absolute', left:'10px', top:'10px', color:'#888'}}>$</span>
                        <input type="number" step="0.01" value={amount} onChange={e=>setAmount(e.target.value)} style={{...inputStyle, paddingLeft:'25px'}} placeholder="0.00" />
                    </div>
                </div>
                <div>
                    <label style={labelStyle}>Vencimiento</label>
                    <input type="date" required value={dueDate} onChange={e=>setDueDate(e.target.value)} style={inputStyle} />
                </div>
                <div>
                    <label style={labelStyle}>Categoría</label>

                    <input 
                        list="category-options" 
                        value={category} 
                        onChange={e=>setCategory(e.target.value)} 
                        style={inputStyle} 
                        placeholder="Seleccionar o escribir..."
                    />
                    <datalist id="category-options">
                        {availableCategories.map((c:string) => <option key={c} value={c} />)}
                    </datalist>

                </div>
            </div>

            {/* 2.2 Configuración */}
            <div style={sectionTitle}>2. Comportamiento</div>
            <div style={rowStyle}>
                 <div>
                    <label style={labelStyle}>Tipo</label>
                    <div style={{display:'flex', gap:'0.5rem'}}>
                        <button type="button" onClick={()=>setType('Fijo')} style={{flex:1, padding:'0.5rem', borderRadius:'6px', border:'1px solid #333', background: type==='Fijo'?'#2563eb':'transparent', color:'white', cursor:'pointer'}}>Fijo</button>
                        <button type="button" onClick={()=>setType('Variable')} style={{flex:1, padding:'0.5rem', borderRadius:'6px', border:'1px solid #333', background: type==='Variable'?'#2563eb':'transparent', color:'white', cursor:'pointer'}}>Variable</button>
                    </div>
                </div>
                <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                    <label style={{...labelStyle, marginBottom:0}}>Auto Pay</label>
                    <input type="checkbox" checked={autoPay} onChange={e=>setAutoPay(e.target.checked)} style={{transform:'scale(1.5)'}} />
                </div>
                 <div style={{gridColumn: 'span 2', background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px'}}>
                    <div style={{display:'flex', justifyContent:'space-between'}}>
                        <label style={{fontSize: '0.9rem'}}>¿Es compra en cuotas?</label>
                        <input type="checkbox" checked={isInstallment} onChange={e=>setIsInstallment(e.target.checked)} />
                    </div>
                    {isInstallment && (
                        <div style={{display:'flex', gap:'1rem', marginTop:'0.5rem'}}>
                            <div>
                                <label style={{fontSize:'0.8rem', color:'#888'}}>Actual</label>
                                <input type="number" value={instCurrent} onChange={e=>setInstCurrent(parseInt(e.target.value))} style={{...inputStyle, padding:'0.4rem'}} />
                            </div>
                            <div style={{display:'flex', alignItems:'end', paddingBottom:'0.5rem', color:'#666'}}>/</div>
                            <div>
                                <label style={{fontSize:'0.8rem', color:'#888'}}>Total</label>
                                <input type="number" value={instTotal} onChange={e=>setInstTotal(parseInt(e.target.value))} style={{...inputStyle, padding:'0.4rem'}} />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* 2.3 Administrativos */}
            <div style={sectionTitle}>3. Datos Administrativos</div>
            <div style={rowStyle}>
                <div>
                     <label style={labelStyle}>Fecha Emisión</label>
                     <input type="date" value={invoiceDate} onChange={e=>setInvoiceDate(e.target.value)} style={inputStyle} />
                </div>
                <div>
                     <label style={labelStyle}>Nº Factura (Opcional)</label>
                     <input type="text" value={invoiceNumber} onChange={e=>setInvoiceNumber(e.target.value)} style={inputStyle} />
                </div>
                <div style={{gridColumn: 'span 2'}}>
                    <label style={labelStyle}>Notas</label>
                    <textarea rows={2} value={notes} onChange={e=>setNotes(e.target.value)} style={{...inputStyle, fontFamily: 'inherit'}} placeholder="Observaciones..." />
                </div>
            </div>

            <div style={{marginTop: '2rem', display: 'flex', gap: '1rem'}}>
                <button type="button" onClick={onClose} style={{flex:1, padding:'1rem', background:'transparent', border:'1px solid #333', color:'#aaa', borderRadius:'8px', cursor:'pointer'}}>Cancelar</button>
                <button type="submit" style={{flex:2, padding:'1rem', background:'#2563eb', border:'none', color:'white', borderRadius:'8px', fontWeight:'bold', cursor:'pointer'}}>
                    {loading ? 'Guardando...' : 'CONFIRMAR REGISTRO'}
                </button>
            </div>

        </form>
      </div>
    </div>
  );
}
