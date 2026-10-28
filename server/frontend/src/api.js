export async function api(path, data) {
  const token=document.cookie.split('; ').find(v=>v.startsWith('csrftoken='))?.split('=')[1] || '';
  const response=await fetch('/djangoapp/'+path,{credentials:'same-origin',
    method:data===undefined?'GET':'POST',
    headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(token)},
    ...(data===undefined?{}:{body:JSON.stringify(data)})});
  const result=await response.json();
  if(!response.ok) throw new Error(result.error || 'Request failed.');
  return result;
}
