import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription, interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { IndexingService } from '../../services/indexing.service';
import { IndexingStatus } from '../../models/indexing.model';

@Component({
  selector: 'app-indexing-status',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="indexing-status">
      <div class="status-header">
        <h4>Indexing Status</h4>
        <span
          class="status-badge"
          [class.status-idle]="!status?.is_indexing"
          [class.status-indexing]="status?.is_indexing">
          {{ status?.is_indexing ? 'In Progress' : 'Idle' }}
        </span>
      </div>

      <div class="status-info">
        <div class="info-row">
          <span class="info-label">Documents:</span>
          <span class="info-value">{{ status?.total_documents || 0 }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Spaces:</span>
          <span class="info-value">{{ status?.total_spaces || 0 }}</span>
        </div>
        <div *ngIf="(status?.last_pii_filtered || 0) > 0" class="info-row pii-info">
          <span class="info-label">PII Filtered:</span>
          <span class="info-value">{{ status?.last_pii_filtered || 0 }} items</span>
        </div>
        <div *ngIf="piiTypesDisplay" class="pii-types">
          {{ piiTypesDisplay }}
        </div>
        <div *ngIf="status?.last_indexed" class="info-row">
          <span class="info-label">Last Indexed:</span>
          <span class="info-value">{{ status?.last_indexed | date:'short' }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div *ngIf="status?.is_indexing && status?.progress" class="progress-section">
        <div class="progress-message">
          {{ status?.progress?.current_message }}
        </div>

        <div *ngIf="(status?.progress?.total_spaces || 0) > 0" class="progress-details">
          <div class="progress-label">
            Spaces: {{ status?.progress?.processed_spaces }} / {{ status?.progress?.total_spaces }}
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              [style.width.%]="getSpacesProgress()">
            </div>
          </div>
        </div>

        <div *ngIf="(status?.progress?.total_documents || 0) > 0" class="progress-details">
          <div class="progress-label">
            Documents: {{ status?.progress?.processed_documents }}
          </div>
        </div>

        <div *ngIf="status?.progress?.current_space" class="current-space">
          Currently indexing: <strong>{{ status?.progress?.current_space }}</strong>
        </div>

        <div *ngIf="status?.progress?.error_message" class="error-message">
          {{ status?.progress?.error_message }}
        </div>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button
          *ngIf="!status?.is_indexing"
          class="btn-primary"
          (click)="startIndexing()"
          [disabled]="isStarting">
          {{ isStarting ? 'Starting...' : '▶️ Start Indexing' }}
        </button>

        <button
          *ngIf="status?.is_indexing"
          class="btn-secondary"
          (click)="stopIndexing()"
          [disabled]="isStopping">
          {{ isStopping ? 'Stopping...' : '⏹️ Stop Indexing' }}
        </button>
      </div>

      <div *ngIf="actionMessage" class="action-message" [class.error]="actionError">
        {{ actionMessage }}
      </div>
    </div>
  `,
  styles: [`
    .indexing-status {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }

    .status-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .status-header h4 {
      font-size: 14px;
      margin: 0;
      color: var(--text-primary);
    }

    .status-badge {
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-size: 11px;
      font-weight: 600;
    }

    .status-idle {
      background-color: var(--secondary-light);
      color: var(--text-secondary);
    }

    .status-indexing {
      background-color: var(--primary-color);
      color: var(--text-on-primary);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }

    .status-info {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
    }

    .info-label {
      color: var(--text-secondary);
    }

    .info-value {
      font-weight: 600;
      color: var(--text-primary);
    }

    .pii-info {
      border-left: 3px solid var(--warning-color);
      padding-left: var(--spacing-xs);
      background-color: rgba(255, 193, 7, 0.1);
      margin: var(--spacing-xs) 0;
      border-radius: var(--radius-sm);
    }

    .pii-types {
      font-size: 10px;
      color: var(--text-tertiary);
      padding: var(--spacing-xs);
      background-color: var(--background-tertiary);
      border-radius: var(--radius-sm);
      margin-top: -4px;
      margin-bottom: var(--spacing-xs);
      font-style: italic;
    }

    .progress-section {
      padding: var(--spacing-sm);
      background-color: var(--background-secondary);
      border-radius: var(--radius-sm);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }

    .progress-message {
      font-size: 12px;
      color: var(--text-primary);
      font-weight: 500;
    }

    .progress-details {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .progress-label {
      font-size: 11px;
      color: var(--text-secondary);
    }

    .progress-bar {
      height: 6px;
      background-color: var(--background-tertiary);
      border-radius: 3px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background-color: var(--primary-color);
      transition: width 0.3s ease;
    }

    .current-space {
      font-size: 11px;
      color: var(--primary-color);
      padding: var(--spacing-xs);
      background-color: var(--background-primary);
      border-radius: var(--radius-sm);
    }

    .error-message {
      font-size: 11px;
      color: var(--error-color);
      padding: var(--spacing-xs);
      background-color: rgba(204, 16, 22, 0.1);
      border-radius: var(--radius-sm);
    }

    .actions {
      display: flex;
      gap: var(--spacing-sm);
    }

    .actions button {
      flex: 1;
      font-size: 12px;
      padding: var(--spacing-sm);
    }

    .action-message {
      font-size: 11px;
      padding: var(--spacing-xs);
      background-color: var(--success-color);
      color: white;
      border-radius: var(--radius-sm);
      text-align: center;
    }

    .action-message.error {
      background-color: var(--error-color);
    }
  `]
})
export class IndexingStatusComponent implements OnInit, OnDestroy {
  status: IndexingStatus | null = null;
  isStarting: boolean = false;
  isStopping: boolean = false;
  actionMessage: string = '';
  actionError: boolean = false;

  private statusSubscription?: Subscription;

  constructor(private indexingService: IndexingService) {}

  ngOnInit(): void {
    this.loadStatus();
    this.startPolling();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  loadStatus(): void {
    this.indexingService.getStatus().subscribe({
      next: (status) => {
        this.status = status;
      },
      error: (error) => {
        console.error('Error loading indexing status:', error);
      }
    });
  }

  startPolling(): void {
    // Poll status every 2 seconds
    this.statusSubscription = interval(2000)
      .pipe(switchMap(() => this.indexingService.getStatus()))
      .subscribe({
        next: (status) => {
          this.status = status;
        },
        error: (error) => {
          console.error('Error polling status:', error);
        }
      });
  }

  stopPolling(): void {
    if (this.statusSubscription) {
      this.statusSubscription.unsubscribe();
    }
  }

  startIndexing(): void {
    this.isStarting = true;
    this.actionMessage = '';
    this.actionError = false;

    this.indexingService.startIndexing().subscribe({
      next: (response) => {
        this.isStarting = false;
        this.actionMessage = 'Indexing started successfully!';
        setTimeout(() => {
          this.actionMessage = '';
        }, 3000);
      },
      error: (error) => {
        console.error('Error starting indexing:', error);
        this.isStarting = false;
        this.actionMessage = 'Failed to start indexing';
        this.actionError = true;
        setTimeout(() => {
          this.actionMessage = '';
          this.actionError = false;
        }, 5000);
      }
    });
  }

  stopIndexing(): void {
    this.isStopping = true;
    this.actionMessage = '';
    this.actionError = false;

    this.indexingService.stopIndexing().subscribe({
      next: (response) => {
        this.isStopping = false;
        this.actionMessage = 'Indexing stopped';
        setTimeout(() => {
          this.actionMessage = '';
        }, 3000);
      },
      error: (error) => {
        console.error('Error stopping indexing:', error);
        this.isStopping = false;
        this.actionMessage = 'Failed to stop indexing';
        this.actionError = true;
        setTimeout(() => {
          this.actionMessage = '';
          this.actionError = false;
        }, 5000);
      }
    });
  }

  getSpacesProgress(): number {
    if (!this.status?.progress || this.status.progress.total_spaces === 0) {
      return 0;
    }
    return (this.status.progress.processed_spaces / this.status.progress.total_spaces) * 100;
  }

  get piiTypesDisplay(): string {
    if (!this.status?.last_pii_by_type) {
      return '';
    }
    return this.getFormattedPIITypes(this.status.last_pii_by_type);
  }

  getFormattedPIITypes(piiByType: { [key: string]: number }): string {
    if (!piiByType || Object.keys(piiByType).length === 0) {
      return '';
    }

    const formatted = Object.entries(piiByType)
      .map(([type, count]) => {
        // Format the type name (e.g., EMAIL_ADDRESS -> Email)
        const formattedType = type
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ');
        return `${formattedType} (${count})`;
      })
      .join(', ');

    return formatted;
  }
}
