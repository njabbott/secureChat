import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConfluenceService } from '../../services/confluence.service';
import { ConfluenceSpace } from '../../models/confluence.model';

@Component({
  selector: 'app-space-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-list">
      <div *ngIf="isLoading" class="loading">
        <div class="spinner"></div>
        <span>Loading spaces...</span>
      </div>

      <div *ngIf="error" class="error-message">
        <span>⚠️ {{ error }}</span>
      </div>

      <div *ngIf="!isLoading && !error && spaces.length === 0" class="empty-state">
        <p>No Confluence spaces found.</p>
      </div>

      <div *ngIf="!isLoading && spaces.length > 0" class="spaces">
        <div *ngFor="let space of spaces" class="space-item">
          <div class="space-info">
            <div class="space-name">{{ space.name }}</div>
          </div>
          <div class="space-count">
            <span class="count-badge">{{ space.document_count }}</span>
            <span class="count-label">docs</span>
          </div>
        </div>
      </div>

      <button
        *ngIf="!isLoading"
        class="refresh-btn"
        (click)="loadSpaces()">
        🔄 Refresh
      </button>
    </div>
  `,
  styles: [`
    .space-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }

    .loading, .error-message, .empty-state {
      padding: var(--spacing-md);
      text-align: center;
      color: var(--text-secondary);
      font-size: 12px;
    }

    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--spacing-sm);
    }

    .error-message {
      background-color: var(--error-color);
      color: white;
      border-radius: var(--radius-sm);
    }

    .spaces {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      max-height: 300px;
      overflow-y: auto;
    }

    .space-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-sm);
      background-color: var(--background-secondary);
      border-radius: var(--radius-sm);
      transition: background-color 0.2s;
      cursor: pointer;
    }

    .space-item:hover {
      background-color: var(--background-tertiary);
    }

    .space-info {
      flex: 1;
      min-width: 0;
    }

    .space-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .space-count {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-left: var(--spacing-sm);
    }

    .count-badge {
      font-size: 14px;
      font-weight: 700;
      color: var(--primary-color);
    }

    .count-label {
      font-size: 10px;
      color: var(--text-tertiary);
    }

    .refresh-btn {
      margin-top: var(--spacing-sm);
      padding: var(--spacing-sm);
      background-color: transparent;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 12px;
      transition: all 0.2s;
      color: var(--text-secondary);
    }

    .refresh-btn:hover {
      background-color: var(--background-tertiary);
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  `]
})
export class SpaceListComponent implements OnInit {
  spaces: ConfluenceSpace[] = [];
  isLoading: boolean = false;
  error: string | null = null;

  constructor(private confluenceService: ConfluenceService) {}

  ngOnInit(): void {
    this.loadSpaces();
  }

  loadSpaces(): void {
    this.isLoading = true;
    this.error = null;

    this.confluenceService.getSpaces().subscribe({
      next: (spaces) => {
        this.spaces = spaces;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading spaces:', error);
        this.error = 'Failed to load Confluence spaces';
        this.isLoading = false;
      }
    });
  }
}
