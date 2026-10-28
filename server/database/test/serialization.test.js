const {test}=require('node:test');
const assert=require('node:assert/strict');
const {clean}=require('../app');
test('API serialization removes Mongo internal fields without losing dealer data',()=>{
  assert.deepEqual(clean({_id:'internal',__v:2,id:15,state:'Kansas'}),{id:15,state:'Kansas'});
});
