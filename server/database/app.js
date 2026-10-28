/* Express service backed by MongoDB; imports starter records without deleting data. */
const express = require('express');
const mongoose = require('mongoose');
const fs = require('node:fs');
const path = require('node:path');
const Dealers = require('./dealership');
const Reviews = require('./review');
const Counter = mongoose.model('counter', new mongoose.Schema({_id:String, value:Number}));
const app = express();
app.use(express.json({limit:'32kb'}));
const asyncRoute = fn => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
const clean = value => { const {_id,__v,...rest}=value; return rest; };
app.get('/', (req,res) => res.json({service:'CarConnect Express-Mongo API',status:'ok'}));
app.get('/fetchDealers', asyncRoute(async(req,res) => res.json((await Dealers.find().sort({id:1}).lean()).map(clean))));
app.get('/fetchDealers/:state', asyncRoute(async(req,res) => res.json((await Dealers.find({state:req.params.state}).sort({id:1}).lean()).map(clean))));
app.get('/fetchDealer/:id', asyncRoute(async(req,res) => res.json((await Dealers.find({id:Number(req.params.id)}).lean()).map(clean))));
app.get('/fetchReviews', asyncRoute(async(req,res) => res.json((await Reviews.find().sort({id:1}).lean()).map(clean))));
app.get('/fetchReviews/dealer/:id', asyncRoute(async(req,res) => res.json((await Reviews.find({dealership:Number(req.params.id)}).sort({id:-1}).lean()).map(clean))));
app.post('/insert_review', asyncRoute(async(req,res) => {
    const body=req.body;
    if(!body.review || typeof body.purchase !== 'boolean' || !Number.isInteger(body.dealership)) return res.status(400).json({error:'Invalid review payload.'});
    const counter = await Counter.findOneAndUpdate({_id:'reviews'},{$inc:{value:1}},{new:true});
    const review = await Reviews.create({id:counter.value,name:body.name,dealership:body.dealership,
        review:body.review,purchase:body.purchase,purchase_date:body.purchase_date || '',
        car_make:body.car_make,car_model:body.car_model,car_year:body.car_year});
    res.status(201).json(clean(review.toObject()));
}));
app.use((error,req,res,next) => {console.error(error.message);res.status(error.name==='ValidationError'?400:500).json({error:'Unable to process request.'});});
async function start(){
    await mongoose.connect(process.env.MONGO_URL || 'mongodb://127.0.0.1:27017/carconnect');
    for (const [Model,file,key] of [[Dealers,'dealerships.json','dealerships'],[Reviews,'reviews.json','reviews']]) {
        const records=JSON.parse(fs.readFileSync(path.join(__dirname,'data',file),'utf8'))[key];
        await Model.bulkWrite(records.map(record=>({updateOne:{filter:{id:record.id},update:{$setOnInsert:record},upsert:true}})));
    }
    const largest=await Reviews.findOne().sort({id:-1}).lean();
    await Counter.updateOne({_id:'reviews'},{$max:{value:largest?.id || 0}},{upsert:true});
    app.listen(process.env.PORT || 3030,'0.0.0.0',()=>console.log('CarConnect Express-Mongo API running on port '+(process.env.PORT || 3030)));
}
if(require.main===module) start().catch(error=>{console.error(error);process.exit(1);});
module.exports={app,clean};
