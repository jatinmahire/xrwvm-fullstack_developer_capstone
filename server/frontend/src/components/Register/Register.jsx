import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {api} from '../../api';
export default function Register({onLogin}) {
  const [form,setForm]=useState({userName:'',firstName:'',lastName:'',email:'',password:''});
  const [error,setError]=useState('');
  const navigate=useNavigate();
  const fields=[['userName','Username','text'],['firstName','First Name','text'],
    ['lastName','Last Name','text'],['email','Email','email'],['password','Password','password']];
  async function submit(event){
    event.preventDefault();setError('');
    try {const result=await api('register',form);onLogin(result.userName);navigate('/');}
    catch(error){setError(error.message);}
  }
  return <section className="form-card"><p className="eyebrow">JOIN CARCONNECT</p><h1>Create your account</h1>
    <p>Share your experience and help other car buyers.</p><form onSubmit={submit}>
    {fields.map(([name,label,type])=><label key={name}>{label}<input name={name} type={type}
      required minLength={name==='password'?8:1} autoComplete={name==='password'?'new-password':undefined}
      value={form[name]} onChange={event=>setForm({...form,[name]:event.target.value})}/></label>)}
    {error && <p role="alert" className="error">{error}</p>}<button type="submit">Register</button>
    </form></section>;
}
