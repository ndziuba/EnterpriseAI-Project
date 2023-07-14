import { NextApiRequest, NextApiResponse } from 'next';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
import fs from 'fs';

export default async function handleFeedback(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { image, latitude, longitude, prediction, feedback, modelVersion } = req.body;
    const dirPath = path.join(process.cwd(), 'data');
    console.log(`Image: ${image}, Latitude: ${latitude}, Longitude: ${longitude}, Prediction: ${prediction}, Feedback: ${feedback}, Model Version: ${modelVersion}`);

    // Check if the directory exists
    if (!fs.existsSync(dirPath)) {
    // If the directory doesn't exist, create it
    fs.mkdirSync(dirPath);
    }

    try {
      // Open a SQLite database
      const db = await open({
        filename: path.join(process.cwd(), 'data', 'feedback.db'),
        driver: sqlite3.Database
      });
      
      // Run a query to create a table if it doesn't exist
      await db.run(`CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image TEXT,
        latitude REAL,
        longitude REAL,
        prediction TEXT,
        feedback INTEGER,
        model_version TEXT
      )`);

      // Insert the feedback into the table
      await db.run(
        'INSERT INTO feedback (image, latitude, longitude, prediction, feedback, model_version) VALUES (?, ?, ?, ?, ?, ?)',
        image,
        latitude,
        longitude, 
        prediction, 
        feedback, 
        modelVersion
      );

      res.status(200).json({ message: 'Feedback received and saved' });

    } catch (e) {
        if (e instanceof Error) {
            res.status(500).json({ message: `Failed to save feedback: ${e.message}` });
          } else {
            res.status(500).json({ message: `Unknown error` });
          }   
    }
  } else {
    res.status(405).json({ message: 'Method Not Allowed' });
  }
}
