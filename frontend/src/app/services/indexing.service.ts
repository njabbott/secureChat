import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { IndexingStatus, IndexingProgress } from '../models/indexing.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class IndexingService {
  private apiUrl = `${environment.apiUrl}/api/indexing`;

  constructor(private http: HttpClient) {}

  startIndexing(): Observable<{ message: string; status: string }> {
    return this.http.post<{ message: string; status: string }>(`${this.apiUrl}/start`, {});
  }

  stopIndexing(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.apiUrl}/stop`, {});
  }

  getStatus(): Observable<IndexingStatus> {
    return this.http.get<IndexingStatus>(`${this.apiUrl}/status`);
  }

  getProgress(): Observable<IndexingProgress> {
    return this.http.get<IndexingProgress>(`${this.apiUrl}/progress`);
  }

  /**
   * Poll for indexing status at regular intervals
   * @param intervalMs Polling interval in milliseconds (default: 2000ms)
   */
  pollStatus(intervalMs: number = 2000): Observable<IndexingStatus> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getStatus())
    );
  }

  /**
   * Poll for indexing progress at regular intervals (only when indexing is in progress)
   * @param intervalMs Polling interval in milliseconds (default: 1000ms)
   */
  pollProgress(intervalMs: number = 1000): Observable<IndexingProgress | null> {
    return interval(intervalMs).pipe(
      startWith(0),
      switchMap(() => this.getProgress())
    );
  }
}
