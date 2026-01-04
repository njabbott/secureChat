import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-about-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-overlay" (click)="closeModal()">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <button class="close-btn" (click)="closeModal()">&times;</button>

        <div class="about-content">
          <h1>About</h1>

          <p class="intro">
            Secure Chat is a sophisticated RAG (Retrieval Augmented Generation) chatbot that searches
            and answers questions from your Confluence documentation, with built-in PII protection.
          </p>

          <p class="designer">Designed and Developed by Nick Abbott.</p>

          <h2>Features</h2>
          <ul>
            <li><strong>Intelligent Search:</strong> Uses OpenAI GPT-4o with RAG to provide accurate answers from your Confluence documentation</li>
            <li><strong>PII Protection:</strong> Automatically detects and filters personally identifiable information using Microsoft Presidio</li>
            <li><strong>Real-time Indexing:</strong> Manual and scheduled indexing with progress tracking</li>
            <li><strong>Source Attribution:</strong> Every answer includes links to source Confluence pages</li>
            <li><strong>Multi-Space Support:</strong> Indexes and searches across all Confluence spaces</li>
            <li><strong>Progress Tracking:</strong> Real-time updates during indexing operations</li>
          </ul>

          <h2>Architecture</h2>

          <h3>Backend (FastAPI + Python)</h3>
          <ul>
            <li><strong>FastAPI:</strong> Modern, fast web framework with automatic API documentation</li>
            <li><strong>ChromaDB:</strong> Vector database for semantic search</li>
            <li><strong>OpenAI:</strong> GPT-4o for chat completions and embeddings</li>
            <li><strong>Microsoft Presidio:</strong> PII detection and anonymisation</li>
            <li><strong>Atlassian Python API:</strong> Confluence integration</li>
            <li><strong>APScheduler:</strong> Scheduled indexing</li>
          </ul>

          <h3>Frontend (Angular)</h3>
          <ul>
            <li><strong>Angular 17:</strong> Modern standalone components</li>
            <li><strong>LinkedIn Colour Palette:</strong> Professional, familiar design</li>
            <li><strong>Responsive Layout:</strong> ChatGPT-inspired interface</li>
            <li><strong>Real-time Updates:</strong> Live progress during indexing</li>
          </ul>

          <div class="github-section">
            <p>View the source code on <a href="https://github.com/njabbott/secureChat" target="_blank" rel="noopener noreferrer">GitHub</a></p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.7);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      padding: var(--spacing-lg);
    }

    .modal-content {
      background-color: var(--background-primary);
      border-radius: var(--radius-lg);
      max-width: 800px;
      max-height: 90vh;
      overflow-y: auto;
      position: relative;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      padding: var(--spacing-xl);
    }

    .close-btn {
      position: absolute;
      top: var(--spacing-md);
      right: var(--spacing-md);
      background: none;
      border: none;
      font-size: 32px;
      cursor: pointer;
      color: var(--text-secondary);
      line-height: 1;
      padding: 0;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-sm);
      transition: all 0.2s;
    }

    .close-btn:hover {
      background-color: var(--background-secondary);
      color: var(--text-primary);
    }

    .about-content {
      color: var(--text-primary);
      line-height: 1.6;
    }

    .about-content h1 {
      font-size: 32px;
      font-weight: 700;
      margin: 0 0 var(--spacing-lg) 0;
      color: var(--primary-color);
    }

    .about-content h2 {
      font-size: 24px;
      font-weight: 600;
      margin: var(--spacing-xl) 0 var(--spacing-md) 0;
      color: var(--primary-color);
    }

    .about-content h3 {
      font-size: 18px;
      font-weight: 600;
      margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
      color: var(--text-primary);
    }

    .intro {
      font-size: 16px;
      margin-bottom: var(--spacing-md);
    }

    .designer {
      font-style: italic;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-lg);
    }

    .about-content ul {
      margin: 0 0 var(--spacing-md) 0;
      padding-left: var(--spacing-lg);
    }

    .about-content li {
      margin-bottom: var(--spacing-sm);
    }

    .about-content li strong {
      color: var(--primary-color);
    }

    .github-section {
      margin-top: var(--spacing-xl);
      padding-top: var(--spacing-lg);
      border-top: 1px solid var(--border-color);
      text-align: center;
    }

    .github-section a {
      color: var(--primary-color);
      text-decoration: none;
      font-weight: 600;
      transition: color 0.2s;
    }

    .github-section a:hover {
      color: var(--primary-dark);
      text-decoration: underline;
    }

    /* Custom scrollbar for modal content */
    .modal-content {
      scrollbar-width: thin;
      scrollbar-color: var(--primary-color) var(--background-secondary);
    }

    .modal-content::-webkit-scrollbar {
      width: 8px;
    }

    .modal-content::-webkit-scrollbar-track {
      background: var(--background-secondary);
      border-radius: 4px;
    }

    .modal-content::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 4px;
    }

    .modal-content::-webkit-scrollbar-thumb:hover {
      background: var(--primary-dark);
    }
  `]
})
export class AboutModalComponent {
  @Output() close = new EventEmitter<void>();

  closeModal(): void {
    this.close.emit();
  }
}