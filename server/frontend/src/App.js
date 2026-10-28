import React,{useEffect,useState} from 'react';
import {Routes,Route,Link,useNavigate,useParams,useSearchParams} from 'react-router-dom';
import Register from './components/Register/Register';
import {api} from './api';

function Login({onLogin}) {
 const [form,setForm]=useState({userName:'',password:''});const [error,setError]=useState('');const nav=useNavigate();
 async function submit(e){e.preventDefault();try{const r=await api('login',form);onLogin(r.userName);nav('/');}catch(e){setError(e.message);}}
 return <section className="form-card"><p className="eyebrow">WELCOME BACK</p><h1>Log in to CarConnect</h1><p>Find your dealer. Share your experience.</p>
 <form onSubmit={submit}><label>Username<input name="username" autoComplete="username" required value={form.userName} onChange={e=>setForm({...form,userName:e.target.value})}/></label>
 <label>Password<input name="password" type="password" autoComplete="current-password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label>
 {error&&<p role="alert" className="error">{error}</p>}<button>Log in</button></form><p>New here? <Link to="/register">Create an account</Link></p></section>;
}
function Dealers({user}) {
 const [rows,setRows]=useState([]),[states,setStates]=useState([]),[error,setError]=useState('');
 const [query,setQuery]=useSearchParams();const state=query.get('state')||'All';
 useEffect(()=>{api('get_dealers').then(r=>setStates([...new Set(r.dealers.map(d=>d.state))].sort())).catch(e=>setError(e.message));},[]);
 useEffect(()=>{api('get_dealers'+(state==='All'?'':'/'+encodeURIComponent(state))).then(r=>setRows(r.dealers)).catch(e=>setError(e.message));},[state]);
 return <><section className="hero"><div><p className="eyebrow">REAL EXPERIENCES. BETTER CHOICES.</p><h1>Find your next trusted dealer.</h1><p>Explore dealerships, read customer experiences and share your own.</p></div>
 <img src="/static/car_dealership.jpg" alt="Car dealership showroom"/></section>
 <section className="panel"><div className="section-heading"><div><h2>Explore dealerships</h2><p>{rows.length} dealerships {state==='All'?'across the United States':'in '+state}</p></div>
 <label className="filter">Filter by state<select aria-label="Filter by state" value={state} onChange={e=>setQuery(e.target.value==='All'?{}:{state:e.target.value})}><option>All</option>{states.map(s=><option key={s}>{s}</option>)}</select></label></div>
 {error&&<p role="alert" className="error">{error}</p>}<div className="table-wrap"><table><thead><tr><th>ID</th><th>Dealer name</th><th>City</th><th>Address</th><th>Zip</th><th>State</th>{user&&<th>Review Dealer</th>}</tr></thead><tbody>
 {rows.map(d=><tr key={d.id}><td>{d.id}</td><td><Link to={'/dealer/'+d.id}>{d.full_name}</Link></td><td>{d.city}</td><td>{d.address}</td><td>{d.zip}</td><td>{d.state}</td>{user&&<td><Link className="small-button" to={'/postreview/'+d.id}>Review Dealer</Link></td>}</tr>)}</tbody></table></div></section></>;
}
function Dealer({user}) {
 const {id}=useParams();const [dealer,setDealer]=useState(null),[reviews,setReviews]=useState([]),[error,setError]=useState('');
 useEffect(()=>{api('dealer/'+id).then(r=>setDealer(r.dealer)).catch(e=>setError(e.message));api('reviews/dealer/'+id).then(r=>setReviews(r.reviews)).catch(e=>setError(e.message));},[id]);
 return <section className="panel"><Link to="/">← All dealerships</Link>{error&&<p role="alert" className="error">{error}</p>}{dealer&&<><p className="eyebrow">DEALER DETAILS • #{dealer.id}</p><h1>{dealer.full_name}</h1><p>{dealer.address}, {dealer.city}, {dealer.state} {dealer.zip}</p>
 {user?<Link className="button" to={'/postreview/'+id}>Review Dealer</Link>:<p><Link to="/login">Log in</Link> to write a review.</p>}<h2>Customer reviews ({reviews.length})</h2>
 <div className="reviews">{reviews.map(r=><article className="review" key={r.id}><span className={'badge '+r.sentiment}>{r.sentiment}</span><h3>{r.name}</h3><p>{r.review}</p><small>{r.car_year} {r.car_make} {r.car_model} · {r.purchase?'Purchased '+r.purchase_date:'No purchase reported'}</small></article>)}</div></>}</section>;
}
function PostReview({user}) {
 const {id}=useParams();const nav=useNavigate();const [dealer,setDealer]=useState(null),[cars,setCars]=useState([]),[error,setError]=useState('');
 const [form,setForm]=useState({dealership:Number(id),review:'',car_id:'',purchase:true,purchase_date:''});
 useEffect(()=>{api('dealer/'+id).then(r=>setDealer(r.dealer)).catch(e=>setError(e.message));api('get_cars').then(r=>setCars(r.cars)).catch(e=>setError(e.message));},[id]);
 async function submit(e){e.preventDefault();try{await api('add_review',form);nav('/dealer/'+id);}catch(e){setError(e.message);}}
 if(!user)return <section className="panel"><h1>Log in to post a review</h1><Link to="/login">Log in</Link></section>;
 return <section className="form-card wide"><p className="eyebrow">SHARE YOUR EXPERIENCE</p><h1>Review {dealer?.full_name || 'dealership'}</h1><p>Posting as <strong>{user}</strong></p>
 <form onSubmit={submit}><label>Your review<textarea name="review" rows="4" required maxLength="5000" value={form.review} onChange={e=>setForm({...form,review:e.target.value})}/></label>
 <label>Car make and model<select name="car_id" required value={form.car_id} onChange={e=>setForm({...form,car_id:e.target.value})}><option value="">Select a vehicle</option>{cars.map(c=><option key={c.id} value={c.id}>{c.make} {c.model} ({c.year})</option>)}</select></label>
 <label className="check"><input type="checkbox" checked={form.purchase} onChange={e=>setForm({...form,purchase:e.target.checked})}/> I purchased a vehicle from this dealer</label>
 {form.purchase&&<label>Purchase date<input type="date" name="purchase_date" required max={new Date().toISOString().slice(0,10)} value={form.purchase_date} onChange={e=>setForm({...form,purchase_date:e.target.value})}/></label>}
 {error&&<p className="error" role="alert">{error}</p>}<button>Submit review</button></form></section>;
}
export default function App(){
 const [user,setUser]=useState(null),[notice,setNotice]=useState('');const nav=useNavigate();
 useEffect(()=>{api('session').then(r=>setUser(r.userName));},[]);
 async function signout(){try{await api('logout',{});setUser(null);setNotice('You have been successfully logged out.');nav('/');}catch(e){setNotice(e.message);}}
 return <><header><Link className="brand" to="/">CarConnect<span>DEALERS & REVIEWS</span></Link><nav><Link to="/">Dealerships</Link><a href="/about/">About Us</a><a href="/contact/">Contact Us</a>{user?<><span className="username">{user}</span><button className="nav-button" onClick={signout}>Log out</button></>:<><Link to="/login">Log in</Link><Link className="button" to="/register">Sign up</Link></>}</nav></header>
 <main>{notice&&<div className="notice" role="alert">{notice}<button aria-label="Dismiss notification" onClick={()=>setNotice('')}>×</button></div>}<Routes><Route path="/" element={<Dealers user={user}/>}/><Route path="/login" element={<Login onLogin={setUser}/>}/><Route path="/register" element={<Register onLogin={setUser}/>}/><Route path="/dealer/:id" element={<Dealer user={user}/>}/><Route path="/postreview/:id" element={<PostReview user={user}/>}/></Routes></main><footer>CarConnect · A dealership review platform · Educational capstone project</footer></>;
}
