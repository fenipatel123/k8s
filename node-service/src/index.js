import express from "express";
import { MongoClient, ObjectId } from "mongodb";

const app = express();
app.use(express.json());

const port = process.env.PORT || 3000;
const mongoUri = process.env.MONGO_URI || "mongodb://mongo:27017/appdb";

app.get("/health", (req,res)=>res.json({status:"ok"}));

app.get("/items", async (req,res)=>{
  let client;
  try{
    client = await MongoClient.connect(mongoUri);
    const items = await client.db().collection("items").find().sort({_id:1}).toArray();
    res.json(items);
  }catch(e){res.status(500).json({error:e.message});}
  finally{ if(client) await client.close(); }
});

app.get("/items/:id", async (req,res)=>{
  let client;
  try{
    client = await MongoClient.connect(mongoUri);
    const item = await client.db().collection("items").findOne({_id:new ObjectId(req.params.id)});
    if(!item) return res.status(404).json({error:"Item not found"});
    res.json(item);
  }catch(e){res.status(400).json({error:e.message});}
  finally{ if(client) await client.close(); }
});

app.post("/items", async (req,res)=>{
  let client;
  try{
    client = await MongoClient.connect(mongoUri);
    const {name,description} = req.body || {};
    if(!name) return res.status(400).json({error:"name is required"});
    const result = await client.db().collection("items").insertOne({name,description,createdAt:new Date()});
    const inserted = await client.db().collection("items").findOne({_id:result.insertedId});
    res.status(201).json(inserted);
  }catch(e){res.status(500).json({error:e.message});}
  finally{ if(client) await client.close(); }
});

app.put("/items/:id", async (req,res)=>{
  let client;
  try{
    client = await MongoClient.connect(mongoUri);
    const {name,description} = req.body || {};
    const result = await client.db().collection("items").findOneAndUpdate(
      {_id:new ObjectId(req.params.id)},
      {$set:{name,description}},
      {returnDocument:"after"}
    );
    if(!result.value) return res.status(404).json({error:"Item not found"});
    res.json(result.value);
  }catch(e){res.status(400).json({error:e.message});}
  finally{ if(client) await client.close(); }
});

app.delete("/items/:id", async (req,res)=>{
  let client;
  try{
    client = await MongoClient.connect(mongoUri);
    const result = await client.db().collection("items").deleteOne({_id:new ObjectId(req.params.id)});
    if(result.deletedCount===0) return res.status(404).json({error:"Item not found"});
    res.status(204).send();
  }catch(e){res.status(400).json({error:e.message});}
  finally{ if(client) await client.close(); }
});

app.listen(port, ()=>console.log(`Node service on ${port}`));
