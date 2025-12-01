/*
  # Create downloads tracking table

  1. New Tables
    - `downloads`
      - `id` (uuid, primary key)
      - `video_title` (text)
      - `video_url` (text)
      - `media_type` (text - 'audio' or 'video')
      - `filename` (text)
      - `file_size` (bigint, optional)
      - `downloaded_at` (timestamp)
      - `status` (text - 'completed', 'failed')

  2. Security
    - Enable RLS on `downloads` table
    - Add policy for public read access (downloads are public records)
    - Add policy for public insert (anonymous users can log downloads)
*/

CREATE TABLE IF NOT EXISTS downloads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_title text NOT NULL,
  video_url text NOT NULL,
  media_type text NOT NULL CHECK (media_type IN ('audio', 'video')),
  filename text NOT NULL,
  file_size bigint,
  downloaded_at timestamptz DEFAULT now(),
  status text DEFAULT 'completed' CHECK (status IN ('completed', 'failed'))
);

ALTER TABLE downloads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Downloads are publicly readable"
  ON downloads FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Anonymous users can log downloads"
  ON downloads FOR INSERT
  TO anon
  WITH CHECK (true);
