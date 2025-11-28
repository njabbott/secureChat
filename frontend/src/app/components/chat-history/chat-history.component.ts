import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

interface HistoryItem {
  id: string;
  title: string;
  timestamp: Date;
  preview: string;
}

@Component({
  selector: 'app-chat-history',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="chat-history">
      <div *ngIf="historyItems.length === 0" class="empty-state">
        <p>No conversation history yet.</p>
        <p class="hint">Start chatting to see your history here.</p>
      </div>

      <div *ngIf="historyItems.length > 0" class="history-list">
        <div *ngFor="let item of historyItems" class="history-item">
          <div class="history-title">{{ item.title }}</div>
          <div class="history-preview">{{ item.preview }}</div>
          <div class="history-time">{{ item.timestamp | date:'short' }}</div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-history {
      display: flex;
      flex-direction: column;
      height: 100%;
    }

    .empty-state {
      padding: var(--spacing-md);
      text-align: center;
      color: var(--text-tertiary);
    }

    .empty-state p {
      font-size: 12px;
      margin-bottom: var(--spacing-xs);
    }

    .hint {
      font-size: 11px;
      font-style: italic;
    }

    .history-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      overflow-y: auto;
    }

    .history-item {
      padding: var(--spacing-sm);
      background-color: var(--background-secondary);
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .history-item:hover {
      background-color: var(--background-tertiary);
    }

    .history-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .history-preview {
      font-size: 11px;
      color: var(--text-secondary);
      margin-bottom: 4px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .history-time {
      font-size: 10px;
      color: var(--text-tertiary);
    }
  `]
})
export class ChatHistoryComponent {
  // In a real implementation, this would be populated from a service
  // For now, it's a placeholder
  historyItems: HistoryItem[] = [];

  constructor() {
    // Example placeholder - in real app, load from backend or localStorage
    // this.historyItems = [
    //   {
    //     id: '1',
    //     title: 'API Documentation',
    //     preview: 'How do I authenticate with the API?',
    //     timestamp: new Date()
    //   }
    // ];
  }
}
