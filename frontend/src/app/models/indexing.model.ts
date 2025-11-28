export type IndexingStatusEnum = 'idle' | 'in_progress' | 'completed' | 'failed';

export interface IndexingProgress {
  status: IndexingStatusEnum;
  current_space?: string;
  total_spaces: number;
  processed_spaces: number;
  total_documents: number;
  processed_documents: number;
  current_message?: string;
  error_message?: string;
  total_pii_filtered?: number;
  pii_by_type?: { [key: string]: number };
}

export interface IndexingStatus {
  last_indexed?: string;
  is_indexing: boolean;
  total_documents: number;
  total_spaces: number;
  next_scheduled_run?: string;
  progress?: IndexingProgress;
  last_pii_filtered?: number;
  last_pii_by_type?: { [key: string]: number };
}
