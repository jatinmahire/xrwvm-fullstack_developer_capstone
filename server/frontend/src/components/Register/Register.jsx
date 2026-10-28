import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {api} from '../../api';
export default function Register({onLogin}) {
  const [form,setForm]=useState({userName:'',firstName:'',lastName:'',email:'',password:''});
  const [error,setError]=useState('');
  const navigate=useNavigate();
  function update(name) {
    return event => setForm({...form, [name]: event.target.value});
  }
  async function submit(event){
    event.preventDefault();setError('');
    try {const result=await api('register',form);onLogin(result.userName);navigate('/');}
    catch(error){setError(error.message);}
  }
  return <section className="form-card"><p className="eyebrow">JOIN CARCONNECT</p><h1>Create your account</h1>
    <p>Share your experience and help other car buyers.</p><form onSubmit={submit}>
    <label>Username
      <input name="userName" type="text" placeholder="Username" required
        autoComplete="username" value={form.userName} onChange={update('userName')}/>
    </label>
    <label>First Name
      <input name="firstName" type="text" placeholder="First Name" required
        autoComplete="given-name" value={form.firstName} onChange={update('firstName')}/>
    </label>
    <label>Last Name
      <input name="lastName" type="text" placeholder="Last Name" required
        autoComplete="family-name" value={form.lastName} onChange={update('lastName')}/>
    </label>
    <label>Email
      <input name="email" type="email" placeholder="email" required
        autoComplete="email" value={form.email} onChange={update('email')}/>
    </label>
    <label>Password
      <input name="password" type="password" placeholder="Password" required minLength={8}
        autoComplete="new-password" value={form.password} onChange={update('password')}/>
    </label>
    {error && <p role="alert" className="error">{error}</p>}<button type="submit">Register</button>
    </form></section>;
}
