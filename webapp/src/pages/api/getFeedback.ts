import { NextApiRequest, NextApiResponse } from 'next';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';

export default async function getFeedback(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const db = await open({
        filename: path.join(process.cwd(), 'data', 'feedback.db'),
        driver: sqlite3.Database
      });

      const feedback = await db.all('SELECT * FROM feedback');
      res.status(200).json(feedback);
    } catch (e) {
      if (e instanceof Error) {
        res.status(500).json({ message: `Failed to fetch feedback: ${e.message}` });
      } else {
        res.status(500).json({ message: `Unknown error` });
      }
    }
  } else {
    res.status(405).json({ message: 'Method Not Allowed' });
  }
}
