export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  sourcesVisible?: boolean;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  chunk_count: number;
}
