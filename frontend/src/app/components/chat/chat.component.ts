import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { JiraService } from '../../services/jira.service';
import { ConversationMessage, JiraTicket } from '../../models/chat.model';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-container">
      <!-- Messages Area -->
      <div class="messages-area" #messagesArea>
        <div *ngIf="messages.length === 0" class="empty-state">
          <h2>Welcome to Secure Chat!</h2>
          <p>Ask me anything about your Confluence documentation.</p>
          <div class="suggestions">
            <button class="suggestion-btn" (click)="useSuggestion('What documentation do we have?')">
              What documentation do we have?
            </button>
            <button class="suggestion-btn" (click)="useSuggestion('Search for API documentation')">
              Search for API documentation
            </button>
          </div>
        </div>

        <div *ngFor="let msg of messages" class="message" [class.user-message]="msg.role === 'user'"
             [class.assistant-message]="msg.role === 'assistant'">
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">{{ msg.role === 'user' ? 'You' : 'Secure Chat' }}</span>
              <span class="message-time">{{ msg.timestamp | date:'short' }}</span>
            </div>
            <div class="message-text">{{ msg.content }}</div>

            <!-- PII Warning -->
            <div *ngIf="msg.pii_filtered" class="pii-warning">
              <span class="warning-icon">⚠️</span>
              <span>{{ msg.pii_info?.total_count }} PII item(s) filtered:
                {{ formatPIIEntities(msg.pii_info?.entities) }}
              </span>
            </div>

            <!-- Sources -->
            <div *ngIf="msg.sources && msg.sources.length > 0" class="sources">
              <div class="sources-header">Sources:</div>
              <div class="source-list">
                <a *ngFor="let source of msg.sources"
                   [href]="source.url"
                   target="_blank"
                   class="source-item">
                  <span class="source-title">{{ source.title }}</span>
                  <span class="source-space">{{ source.space }}</span>
                </a>
              </div>
            </div>

            <!-- Jira ticket created card -->
            <div *ngIf="msg.jiraTicket" class="jira-ticket-card">
              <div class="jira-ticket-header">
                <span class="jira-check">&#10003;</span> Jira ticket created
              </div>
              <div class="jira-ticket-body">
                <span class="jira-key">{{ msg.jiraTicket.key }}</span>
                <span class="jira-type">{{ msg.jiraTicket.issue_type }}</span>
              </div>
              <div class="jira-ticket-summary">{{ msg.jiraTicket.summary }}</div>
              <a [href]="msg.jiraTicket.url" target="_blank" class="jira-ticket-link">
                View in Jira &#8594;
              </a>
            </div>

            <!-- Offer to create a ticket when no docs found -->
            <div *ngIf="msg.suggestTicket && !msg.jiraTicket" class="jira-suggest">
              <span class="jira-suggest-text">No documentation found. Want to log this as a Jira ticket?</span>
              <button class="jira-suggest-btn"
                      [disabled]="msg.creatingTicket"
                      (click)="createTicketFromSuggestion(msg)">
                <span *ngIf="!msg.creatingTicket">&#128203; Create Jira Ticket</span>
                <span *ngIf="msg.creatingTicket" class="spinner"></span>
              </button>
            </div>
          </div>
        </div>

        <div *ngIf="isLoading" class="message assistant-message loading-message">
          <div class="message-content">
            <div class="message-header">
              <span class="message-role">Secure Chat</span>
            </div>
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <div class="input-container">
          <textarea
            [(ngModel)]="userInput"
            (keydown.enter)="onEnterKey($event)"
            placeholder="Ask about your Confluence documentation..."
            [disabled]="isLoading"
            rows="1"
          ></textarea>
          <button
            class="send-btn"
            (click)="sendMessage()"
            [disabled]="!userInput.trim() || isLoading">
            <span *ngIf="!isLoading">Send</span>
            <span *ngIf="isLoading" class="spinner"></span>
          </button>
        </div>
        <div class="input-hint">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: var(--background-secondary);
      overflow: hidden; /* Prevent container from growing */
    }

    .messages-area {
      flex: 1 1 auto;
      min-height: 0; /* Allow flex item to shrink below content size */
      overflow-y: auto;
      overflow-x: hidden;
      padding: var(--spacing-lg);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
      /* Custom scrollbar styling */
      scrollbar-width: thin;
      scrollbar-color: var(--primary-color) var(--background-primary);
    }

    .messages-area::-webkit-scrollbar {
      width: 8px;
    }

    .messages-area::-webkit-scrollbar-track {
      background: var(--background-primary);
      border-radius: 4px;
    }

    .messages-area::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 4px;
    }

    .messages-area::-webkit-scrollbar-thumb:hover {
      background: var(--primary-dark);
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      color: var(--text-secondary);
    }

    .empty-state h2 {
      color: var(--primary-color);
      margin-bottom: var(--spacing-sm);
    }

    .suggestions {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      margin-top: var(--spacing-lg);
    }

    .suggestion-btn {
      padding: var(--spacing-md);
      background-color: var(--background-primary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.2s;
      color: var(--text-primary);
    }

    .suggestion-btn:hover {
      border-color: var(--primary-color);
      box-shadow: 0 2px 8px var(--shadow);
    }

    .message {
      display: flex;
      margin-bottom: var(--spacing-md);
    }

    .user-message {
      justify-content: flex-end;
    }

    .assistant-message {
      justify-content: flex-start;
    }

    .message-content {
      max-width: 70%;
      padding: var(--spacing-md);
      border-radius: var(--radius-md);
      background-color: var(--background-primary);
      box-shadow: 0 1px 2px var(--shadow);
    }

    .user-message .message-content {
      background-color: var(--primary-color);
      color: var(--text-on-primary);
    }

    .message-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: var(--spacing-xs);
      font-size: 12px;
    }

    .message-role {
      font-weight: 600;
    }

    .user-message .message-role {
      color: var(--text-on-primary);
    }

    .message-time {
      opacity: 0.7;
    }

    .message-text {
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .pii-warning {
      margin-top: var(--spacing-sm);
      padding: var(--spacing-sm);
      background-color: var(--warning-color);
      border-radius: var(--radius-sm);
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
    }

    .warning-icon {
      font-size: 16px;
    }

    .sources {
      margin-top: var(--spacing-md);
      padding-top: var(--spacing-sm);
      border-top: 1px solid var(--border-color);
    }

    .sources-header {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-xs);
    }

    .source-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
    }

    .source-item {
      display: flex;
      flex-direction: column;
      padding: var(--spacing-xs);
      background-color: var(--background-secondary);
      border-radius: var(--radius-sm);
      text-decoration: none;
      color: var(--primary-color);
      font-size: 12px;
      transition: background-color 0.2s;
    }

    .source-item:hover {
      background-color: var(--background-tertiary);
    }

    .source-title {
      font-weight: 600;
    }

    .source-space {
      font-size: 11px;
      color: var(--text-tertiary);
    }

    .loading-message .message-content {
      background-color: var(--background-primary);
    }

    .typing-indicator {
      display: flex;
      gap: 4px;
      padding: var(--spacing-sm) 0;
    }

    .typing-indicator span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--secondary-color);
      animation: typing 1.4s infinite;
    }

    .typing-indicator span:nth-child(2) {
      animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes typing {
      0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
      30% { transform: translateY(-10px); opacity: 1; }
    }

    .input-area {
      flex-shrink: 0; /* Prevent input area from shrinking */
      padding: var(--spacing-lg);
      padding-bottom: calc(var(--spacing-lg) + 0.5cm); /* ~1cm from bottom */
      background-color: var(--background-primary);
      border-top: 1px solid var(--border-color);
      box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05); /* Subtle shadow for depth */
    }

    .input-container {
      display: flex;
      gap: var(--spacing-sm);
      align-items: flex-end;
    }

    .input-container textarea {
      flex: 1;
      max-height: 200px;
      padding: var(--spacing-md);
      resize: none;
    }

    .send-btn {
      padding: var(--spacing-md) var(--spacing-lg);
      background-color: var(--primary-color);
      color: var(--text-on-primary);
      border: none;
      border-radius: var(--radius-md);
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.2s;
      min-width: 80px;
    }

    .send-btn:hover:not(:disabled) {
      background-color: var(--primary-dark);
    }

    .send-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .input-hint {
      margin-top: var(--spacing-xs);
      font-size: 11px;
      color: var(--text-tertiary);
    }

    .jira-ticket-card {
      margin-top: var(--spacing-md);
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1.5px solid #2d8a4e;
      border-radius: var(--radius-sm);
      background-color: #f0faf4;
      font-size: 13px;
    }

    .jira-ticket-header {
      font-weight: 600;
      color: #2d8a4e;
      margin-bottom: var(--spacing-xs);
    }

    .jira-check {
      font-size: 15px;
    }

    .jira-ticket-body {
      display: flex;
      gap: var(--spacing-sm);
      align-items: center;
      margin-bottom: 2px;
    }

    .jira-key {
      font-weight: 700;
      color: #0a66c2;
    }

    .jira-type {
      font-size: 11px;
      color: var(--text-secondary);
      background-color: #e8f0fe;
      padding: 1px 6px;
      border-radius: 10px;
    }

    .jira-ticket-summary {
      color: var(--text-primary);
      margin-bottom: var(--spacing-xs);
    }

    .jira-ticket-link {
      font-size: 12px;
      color: #0a66c2;
      text-decoration: none;
    }

    .jira-ticket-link:hover {
      text-decoration: underline;
    }

    .jira-suggest {
      margin-top: var(--spacing-md);
      padding: var(--spacing-sm) var(--spacing-md);
      border: 1px dashed var(--border-color);
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      flex-wrap: wrap;
    }

    .jira-suggest-text {
      font-size: 13px;
      color: var(--text-secondary);
      flex: 1;
    }

    .jira-suggest-btn {
      padding: var(--spacing-xs) var(--spacing-md);
      background-color: #0a66c2;
      color: #fff;
      border: none;
      border-radius: var(--radius-sm);
      font-size: 13px;
      cursor: pointer;
      white-space: nowrap;
      transition: background-color 0.2s;
      min-width: 160px;
    }

    .jira-suggest-btn:hover:not(:disabled) {
      background-color: #004182;
    }

    .jira-suggest-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  `]
})
export class ChatComponent implements OnInit {
  messages: (ConversationMessage & { creatingTicket?: boolean })[] = [];
  userInput: string = '';
  isLoading: boolean = false;
  sessionId: string;

  constructor(private chatService: ChatService, private jiraService: JiraService) {
    this.sessionId = this.generateSessionId();
  }

  ngOnInit(): void {
    // Could load chat history here if implementing persistence
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.isLoading) {
      return;
    }

    const userMessage: ConversationMessage = {
      role: 'user',
      content: this.userInput,
      timestamp: new Date()
    };

    this.messages.push(userMessage);
    const query = this.userInput;
    this.userInput = '';
    this.isLoading = true;

    this.chatService.sendMessage({
      message: query,
      session_id: this.sessionId
    }).subscribe({
      next: (response) => {
        const assistantMessage: ConversationMessage = {
          role: 'assistant',
          content: response.response,
          timestamp: new Date(response.timestamp),
          sources: response.sources,
          pii_filtered: response.pii_filtered,
          pii_info: response.pii_info,
          jiraTicket: response.jira_ticket,
          suggestTicket: response.suggest_ticket,
          originalQuestion: query,
        };

        this.messages.push(assistantMessage);
        this.isLoading = false;
        this.scrollToBottom();
      },
      error: (error) => {
        console.error('Error sending message:', error);
        const errorMessage: ConversationMessage = {
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your request. Please try again.',
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
        this.isLoading = false;
      }
    });

    this.scrollToBottom();
  }

  onEnterKey(event: any): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  useSuggestion(suggestion: string): void {
    this.userInput = suggestion;
    this.sendMessage();
  }

  formatPIIEntities(entities?: { [key: string]: number }): string {
    if (!entities) return '';
    return Object.entries(entities)
      .map(([type, count]) => `${type} (${count})`)
      .join(', ');
  }

  createTicketFromSuggestion(msg: ConversationMessage & { creatingTicket?: boolean }): void {
    msg.creatingTicket = true;
    this.jiraService.createTicket({
      summary: msg.originalQuestion || 'Unanswered question from Secure Chat',
      description: msg.content,
      issue_type: 'Question',
      priority: 'Medium',
    }).subscribe({
      next: (ticket: JiraTicket) => {
        msg.jiraTicket = ticket;
        msg.suggestTicket = false;
        msg.creatingTicket = false;
      },
      error: (err: any) => {
        console.error('Failed to create Jira ticket:', err);
        msg.creatingTicket = false;
      }
    });
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const messagesArea = document.querySelector('.messages-area');
      if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
      }
    }, 100);
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
