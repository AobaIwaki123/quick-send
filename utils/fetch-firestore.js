// direct-export.js
const admin = require('firebase-admin');
const fs = require('fs').promises;

const serviceAccount = require('../creds/th-zenn-ai-hackathon-4ac7224d35fd.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

async function getAllCollections() {
  const collections = await db.listCollections();
  const allData = {};
  
  for (const collectionRef of collections) {
    console.log(`Exporting collection: ${collectionRef.id}`);
    const snapshot = await collectionRef.get();
    
    allData[collectionRef.id] = await Promise.all(
      snapshot.docs.map(async (doc) => {
        const data = { id: doc.id, ...doc.data() };
        
        // サブコレクションも取得
        const subcollections = await doc.ref.listCollections();
        for (const subcol of subcollections) {
          const subSnapshot = await subcol.get();
          data[subcol.id] = subSnapshot.docs.map(d => ({
            id: d.id,
            ...d.data()
          }));
        }
        
        return data;
      })
    );
  }
  
  return allData;
}

async function exportToJson() {
  try {
    const data = await getAllCollections();
    await fs.writeFile(
      'utils/example.json',
      JSON.stringify(data, null, 2)
    );
    console.log('✓ Export complete! Saved to firestore-complete.json');
  } catch (error) {
    console.error('Error:', error);
  }
}

exportToJson();