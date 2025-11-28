import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatComponent } from './components/chat/chat.component';
import { SpaceListComponent } from './components/space-list/space-list.component';
import { ChatHistoryComponent } from './components/chat-history/chat-history.component';
import { IndexingStatusComponent } from './components/indexing-status/indexing-status.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    ChatComponent,
    SpaceListComponent,
    ChatHistoryComponent,
    IndexingStatusComponent
  ],
  template: `
    <div class="app-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h1 class="app-title">Secure Chat</h1>
          <p class="app-subtitle">Chatbot for the Intranet, with Privacy Protection</p>
        </div>

        <!-- Indexing Status -->
        <div class="sidebar-section">
          <app-indexing-status></app-indexing-status>
        </div>

        <!-- Confluence Spaces -->
        <div class="sidebar-section">
          <h3>Confluence Spaces</h3>
          <app-space-list></app-space-list>
        </div>

        <!-- Chat History -->
        <div class="sidebar-section flex-grow">
          <h3>Recent Conversations</h3>
          <app-chat-history></app-chat-history>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <app-chat></app-chat>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    .sidebar {
      width: 300px;
      background-color: var(--background-primary);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }

    .sidebar-header {
      padding: var(--spacing-lg);
      border-bottom: 1px solid var(--border-color);
      background-color: var(--primary-color);
      color: var(--text-on-primary);
    }

    .app-title {
      font-size: 24px;
      font-weight: 700;
      margin: 0;
      color: var(--text-on-primary);
    }

    .app-subtitle {
      font-size: 12px;
      margin: var(--spacing-xs) 0 0 0;
      opacity: 0.9;
      color: var(--text-on-primary);
    }

    .sidebar-section {
      padding: var(--spacing-md);
      border-bottom: 1px solid var(--border-color);
    }

    .sidebar-section.flex-grow {
      flex-grow: 1;
      overflow-y: auto;
    }

    .sidebar-section h3 {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: var(--spacing-sm);
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .main-content app-chat {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      overflow: hidden;
    }

    @media (max-width: 768px) {
      .sidebar {
        display: none;
      }
    }
  `]
})
export class AppComponent {
  title = 'Secure Chat';
}
