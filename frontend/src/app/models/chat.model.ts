export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface PIIInfo {
  total_count: number;
  entities: { [key: string]: number };
}

export interface Source {
  title: string;
  space: string;
  url: string;
}

export interface ChatResponse {
  response: string;
  sources: Source[];
  pii_filtered: boolean;
  pii_info?: PIIInfo;
  session_id?: string;
  timestamp: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  pii_filtered?: boolean;
  pii_info?: PIIInfo;
}
