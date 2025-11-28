import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfluenceSpace } from '../models/confluence.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConfluenceService {
  private apiUrl = `${environment.apiUrl}/api/confluence`;

  constructor(private http: HttpClient) {}

  getSpaces(): Observable<ConfluenceSpace[]> {
    return this.http.get<ConfluenceSpace[]>(`${this.apiUrl}/spaces`);
  }

  getSpaceDocumentCount(spaceKey: string): Observable<{ space_key: string; document_count: number }> {
    return this.http.get<{ space_key: string; document_count: number }>(
      `${this.apiUrl}/spaces/${spaceKey}/count`
    );
  }
}
